'use client'

import { useEffect, useRef } from 'react'
import { Box, Flex, Text, HoverCard, Button } from '@radix-ui/themes'
import { QuestionMarkCircledIcon } from '@radix-ui/react-icons'

type GameContentDisplayProps = {
  content: string
  name?: string
  description?: string
  showName?: boolean
}

export const GameContentDisplay: React.FC<GameContentDisplayProps> = ({
  content,
  name,
  description,
  showName
}) => {
  const contentEndRef = useRef<null | HTMLDivElement>(null)

  const scrollToBottom = () => {
    contentEndRef.current?.scrollIntoView()
  }

  useEffect(() => {
    scrollToBottom()
  }, [content])

  return (
    <Flex gap='2' direction='column' className='w-2/6 grow'>
      {showName && name && (
        <Flex gap='1' align='baseline' justify='center'>
          {name}
          {description && (
            <HoverCard.Root>
              <HoverCard.Trigger>
                <QuestionMarkCircledIcon color='gray' />
              </HoverCard.Trigger>
              <HoverCard.Content maxWidth='300px'>
                <Text as='div' size='2'>
                  {description}
                </Text>
              </HoverCard.Content>
            </HoverCard.Root>
          )}
        </Flex>
      )}
      <Box className='bg-white overflow-y-scroll w-full p-4 whitespace-pre-wrap grow rounded shadow-md outline outline-gray-300 outline-1'>
        {content}
        <div ref={contentEndRef} />
      </Box>
    </Flex>
  )
}
