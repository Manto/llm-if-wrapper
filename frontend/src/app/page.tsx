'use client'

import { useState, useEffect, useRef } from 'react'
import {
  Dialog,
  Flex,
  Button,
  Text,
  Heading,
  Select,
  Code,
  Box,
  Switch,
  TextField
} from '@radix-ui/themes'

const GAMES = [
  { id: '905.z5', label: '9:05 by Adam Cadre' },
  { id: 'lostpig.z8', label: 'Lost Pig by Admiral Jota' },
  { id: 'zork1.z5', label: 'Zork I' }
]

const TONES = [
  { id: 'pratchett', label: 'Cheeky' },
  { id: 'original', label: 'Original' },
  { id: 'gumshoe', label: 'Hard Boiled' },
  { id: 'hardyboys', label: 'YA Mysteries' },
  { id: 'spaceopera', label: 'Space Opera' }
]

const LLMS = [
  { id: 'anthropic', label: 'Claude 3.5 Sonnet' },
  { id: 'hosted', label: 'Hosted' }
]

const API_URL = 'https://manto--llm-text-adv-web-dev.modal.run'

const App = () => {
  const [game, setGame] = useState(GAMES[0].id)
  const [tone, setTone] = useState(TONES[0].id)
  const [llm, setLlm] = useState(LLMS[0].id)
  const [isStartGameOpen, setIsStartGameOpen] = useState(false)
  const [isStartingGame, setIsStartingGame] = useState(false)
  const [isProcessingCommand, setIsProcessingCommand] = useState(false)
  const [showOriginal, setShowOriginal] = useState(true)
  const [showDebug, setShowDebug] = useState(false)
  const [gameStateId, setGameStateId] = useState()
  const [command, setCommand] = useState('')
  const [debug, setDebug] = useState('')
  const [gameText, setGameText] = useState('')
  const [originalText, setOriginalText] = useState('')
  const mounted = useRef(false)

  const onMount = async () => {
    // Warm up LLM functions before player begin to start game
    fetch(`${API_URL}/warm_inference`, { method: 'POST' })
  }

  useEffect(() => {
    // Prevents calling this twice in local dev
    if (!mounted.current) {
      mounted.current = true
      onMount()
    }
  }, [])

  const startGame = async () => {
    setIsStartingGame(true)

    try {
      const response = await fetch(`${API_URL}/start_game`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          game_id: game,
          tone: tone,
          llm_provider: llm
        })
      })
      const data = await response.json()
      setGameStateId(data['id'])
      setGameText(gameText + '\n' + data['llm_response'] + '\n')
      setOriginalText(originalText + '\n' + data['game_response'] + '\n')
    } finally {
      setIsStartingGame(false)
      setIsStartGameOpen(false)
    }
  }

  const processCommand = async () => {
    setIsProcessingCommand(true)
    try {
      const response = await fetch(`${API_URL}/user_command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          game_id: gameStateId,
          input: command
        })
      })

      const data = await response.json()
      setOriginalText(
        `${originalText}\n> ${data['game_command']}\n\n${data['game_response']}\n`
      )
      setGameText(
        `${gameText}\n> ${data['input_command']}\n\n${data['llm_response']}\n`
      )
      setCommand('')
    } finally {
      setIsProcessingCommand(false)
    }
  }

  const onCommandKeyUp = (e: React.KeyboardEvent) => {
    if (e.code === 'Enter') {
      processCommand()
    }
  }

  return (
    <>
      {!gameStateId && (
        <div className='min-w-full min-h-screen bg-gray-100 screen flex flex-col gap-6 justify-center items-center'>
          <Heading>LLM-IF-Wrapper</Heading>
          <Button onClick={() => setIsStartGameOpen(true)} size='4'>
            Start Game
          </Button>

          <Dialog.Root open={isStartGameOpen}>
            <Dialog.Content maxWidth='450px'>
              <Dialog.Title>Start Game</Dialog.Title>
              <Dialog.Description size='2' mb='4'>
                Select a game and a tone for the story.
              </Dialog.Description>

              <Flex direction='column' gap='3'>
                <label>
                  <Text as='div' size='2' mb='1' weight='bold'>
                    Game
                  </Text>
                  <Select.Root defaultValue={game} onValueChange={setGame}>
                    <Select.Trigger />
                    <Select.Content>
                      <Select.Group>
                        {GAMES.map((entry, i) => {
                          return (
                            <Select.Item
                              key={i}
                              value={entry.id}
                              onSelect={() => {
                                setGame(entry.id)
                              }}
                            >
                              {entry.label}
                            </Select.Item>
                          )
                        })}
                      </Select.Group>
                    </Select.Content>
                  </Select.Root>
                </label>
                <label>
                  <Text as='div' size='2' mb='1' weight='bold'>
                    Tone
                  </Text>
                  <Select.Root defaultValue={tone} onValueChange={setTone}>
                    <Select.Trigger />
                    <Select.Content>
                      <Select.Group>
                        {TONES.map((entry, i) => {
                          return (
                            <Select.Item key={i} value={entry.id}>
                              {entry.label}
                            </Select.Item>
                          )
                        })}
                      </Select.Group>
                    </Select.Content>
                  </Select.Root>
                </label>
                <label>
                  <Text as='div' size='2' mb='1' weight='bold'>
                    LLM
                  </Text>
                  <Select.Root defaultValue={llm} onValueChange={setLlm}>
                    <Select.Trigger />
                    <Select.Content>
                      <Select.Group>
                        {LLMS.map((entry, i) => {
                          return (
                            <Select.Item key={i} value={entry.id}>
                              {entry.label}
                            </Select.Item>
                          )
                        })}
                      </Select.Group>
                    </Select.Content>
                  </Select.Root>
                  {llm === 'anthropic' && (
                    <Box>
                      <Text size='1'>
                        Make sure you provided a valid{' '}
                        <Code>ANTHROPIC_API_KEY</Code>
                        in <Code>.env</Code> file for your deployed Modal
                        endpoint.
                      </Text>
                    </Box>
                  )}
                </label>
              </Flex>

              <Flex gap='3' mt='4' justify='end'>
                <Button
                  onClick={() => setIsStartGameOpen(false)}
                  variant='soft'
                  color='gray'
                >
                  Cancel
                </Button>
                <Button loading={isStartingGame} onClick={startGame}>
                  Start
                </Button>
              </Flex>
            </Dialog.Content>
          </Dialog.Root>
        </div>
      )}

      {gameStateId && (
        <Flex
          direction='column'
          gap='4'
          className='min-w-full min-h-screen bg-gray-100 screen'
        >
          <Flex align='center' className='p-3 bg-gray-300 w-full'>
            <Flex gap='3' className='p-1 grow'>
              <Text>
                Game: <Code>{game}</Code>
              </Text>
              <Text>
                Writing Style: <Code>{tone}</Code>
              </Text>
              <Text>
                LLM: <Code>{llm}</Code>
              </Text>
              <Text>
                Game State ID: <Code>{gameStateId}</Code>
              </Text>
            </Flex>
            <Flex gap='4' align='center' className='p-1'>
              <Flex gap='2'>
                <Text size='1'>Show Original</Text>
                <Switch
                  defaultChecked
                  radius='small'
                  size='1'
                  onCheckedChange={setShowOriginal}
                />
              </Flex>
              <Flex gap='2'>
                <Text size='1'>Show Debug</Text>
                <Switch
                  radius='small'
                  size='1'
                  onCheckedChange={setShowDebug}
                />
              </Flex>
            </Flex>
          </Flex>
          <Flex className='min-w-full max-h-[600px] min-h-[400px] bg-gray-100 screen flex flex-row gap-4 pl-4 pr-4'>
            {showOriginal && <GameContentDisplay content={originalText} />}
            <GameContentDisplay content={gameText} />
            {showDebug && <GameContentDisplay content={debug} />}
          </Flex>
          <Box className='bg-white'>
            <TextField.Root
              value={command}
              disabled={isProcessingCommand}
              onChange={e => setCommand(e.currentTarget.value)}
              onKeyUp={onCommandKeyUp}
              className='m-8'
              placeholder='What do you do next?'
              size='3'
            >
              <TextField.Slot>{isProcessingCommand && <>⌛</>}</TextField.Slot>
            </TextField.Root>
          </Box>
        </Flex>
      )}
    </>
  )
}

const GameContentDisplay = ({ content }: { content: string }) => {
  const contentEndRef = useRef<null | HTMLDivElement>(null)

  useEffect(() => {
    setTimeout(
      () => contentEndRef.current?.scrollIntoView({ behavior: 'smooth' }),
      100
    )
  }, [content])

  return (
    <Box className='bg-white overflow-y-scroll w-2/6 p-4 whitespace-pre-wrap grow rounded shadow-md outline outline-gray-300 outline-1'>
      {content}
      <div ref={contentEndRef} />
    </Box>
  )
}

export default App
