'use client'

import { useState, useEffect, useRef, ReactNode } from 'react'
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
import { GameContentDisplay } from './gameDisplay'
import { StopwatchIcon } from '@radix-ui/react-icons'

import { GAMES, TONES, LLMS, API_URL } from './settings'

const App = () => {
  const [game, setGame] = useState(GAMES[0].id)
  const [tone, setTone] = useState(TONES[0].id)
  const [llm, setLlm] = useState(LLMS[0].id)
  const [isStartGameOpen, setIsStartGameOpen] = useState(false)
  const [isStartingGame, setIsStartingGame] = useState(false)
  const [isTailingLog, setIsTailingLog] = useState(false)
  const [isProcessingCommand, setIsProcessingCommand] = useState(false)
  const [visibleSections, setVisibleSections] = useState(['game', 'original'])
  const [gameStateId, setGameStateId] = useState()
  const [command, setCommand] = useState('')
  const [debug, setDebug] = useState<string>()
  const [gameText, setGameText] = useState<any[]>([])
  const [originalText, setOriginalText] = useState<any[]>([])
  const commandInputRef = useRef<null | HTMLInputElement>(null)
  const mounted = useRef(false)
  const pollLogId = useRef<ReturnType<typeof setInterval>>()

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

  useEffect(() => {
    if (gameStateId) {
      tailLog()
    }
  }, [gameStateId])

  useEffect(() => {
    if (isProcessingCommand && visibleSections.indexOf('debug')) {
      pollLogId.current = setInterval(() => {
        tailLog()
      }, 5000)
    } else {
      clearInterval(pollLogId.current)
    }

    return () => clearInterval(pollLogId.current)
  }, [isProcessingCommand])

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
      setGameText([
        ...gameText,
        <span key={gameText.length}>{data['llm_response']}</span>
      ])
      setOriginalText([
        ...originalText,
        <span key={originalText.length}>{data['game_response']}</span>
      ])
    } finally {
      setIsStartingGame(false)
      setIsStartGameOpen(false)
    }
  }

  const tailLog = async () => {
    setIsTailingLog(true)

    try {
      const response = await fetch(`${API_URL}/tail_log`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          game_state_id: gameStateId
        })
      })
      const result = await response.json()
      setDebug(result.log)
    } finally {
      setIsTailingLog(false)
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
      setOriginalText([
        ...originalText,
        <span key={originalText.length}>
          <b>&gt; {data['game_command']}</b>
        </span>,
        <span key={originalText.length + 1}>{data['game_response']}</span>
      ])
      setGameText([
        ...gameText,
        <span key={gameText.length}>
          <b>&gt; {data['input_command']}</b>
        </span>,
        <span key={gameText.length + 1}>{data['llm_response']}</span>
      ])
      setCommand('')
    } finally {
      setIsProcessingCommand(false)
      setTimeout(() => commandInputRef.current?.focus(), 20)
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
                Select a game and a rewrite tone for the story.
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
                    Rewrite Tone
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
                  onCheckedChange={() => {
                    if (visibleSections.indexOf('original') === -1) {
                      setVisibleSections([...visibleSections, 'original'])
                    } else {
                      setVisibleSections(
                        visibleSections.filter(s => s !== 'original')
                      )
                    }
                  }}
                />
              </Flex>
              <Flex gap='2'>
                <Text size='1'>Show Debug</Text>
                <Switch
                  radius='small'
                  size='1'
                  onCheckedChange={() => {
                    if (visibleSections.indexOf('debug') === -1) {
                      setVisibleSections([...visibleSections, 'debug'])
                    } else {
                      setVisibleSections(
                        visibleSections.filter(s => s !== 'debug')
                      )
                    }
                  }}
                />
              </Flex>
            </Flex>
          </Flex>
          <Flex className='min-w-full max-h-[600px] min-h-[400px] bg-gray-100 screen flex flex-row gap-4 pl-4 pr-4'>
            {visibleSections.indexOf('original') !== -1 && (
              <GameContentDisplay
                visibleSections={visibleSections}
                name='Original Game Text'
                description='This is how the game content looks as originally designed and written by the creator.'
              >
                <>{originalText}</>
              </GameContentDisplay>
            )}
            {visibleSections.indexOf('game') !== -1 && (
              <GameContentDisplay
                visibleSections={visibleSections}
                name='LLM Wrapped Game Text'
                description='This is how the game content looks with LLM parsing and rewrite.'
              >
                <>{gameText}</>
              </GameContentDisplay>
            )}
            {visibleSections.indexOf('debug') !== -1 && (
              <GameContentDisplay
                name='Debug Log'
                visibleSections={visibleSections}
              >
                <Code size='1'>{debug}</Code>
              </GameContentDisplay>
            )}
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
              ref={commandInputRef}
            >
              <TextField.Slot>
                {isProcessingCommand && <StopwatchIcon />}
              </TextField.Slot>
            </TextField.Root>
          </Box>
        </Flex>
      )}
    </>
  )
}

export default App
