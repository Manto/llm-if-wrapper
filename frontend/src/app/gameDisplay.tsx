'use client'

import { ReactNode, useEffect, useRef } from 'react'
import { Box, Flex, Text, HoverCard, Button } from '@radix-ui/themes'
import { QuestionMarkCircledIcon } from '@radix-ui/react-icons'

type GameContentDisplayProps = {
  visibleSections: string[]
  name?: string
  description?: string
  children?: JSX.Element
}

export const GameContentDisplay: React.FC<GameContentDisplayProps> = ({
  name,
  description,
  visibleSections,
  children
}) => {
  const contentEndRef = useRef<null | HTMLDivElement>(null)

  const scrollToBottom = () => {
    contentEndRef.current?.scrollIntoView()
  }

  useEffect(() => {
    scrollToBottom()
  }, [children, visibleSections])

  return (
    <Flex gap='2' direction='column' className='w-2/6 grow'>
      {visibleSections.length > 1 && name && (
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
      <Flex
        gap='4'
        direction='column'
        className='bg-white overflow-y-scroll w-full p-4 whitespace-pre-wrap grow rounded shadow-md outline outline-gray-300 outline-1'
      >
        {children}
        <div ref={contentEndRef} />
      </Flex>
    </Flex>
  )
}
