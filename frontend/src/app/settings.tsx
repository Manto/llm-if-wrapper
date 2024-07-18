export const GAMES = [
  { id: '905.z5', label: '9:05 by Adam Cadre' },
  { id: 'lostpig.z8', label: 'Lost Pig by Admiral Jota' },
  { id: 'zork1.z5', label: 'Zork I' }
]

export const TONES = [
  {
    id: 'pratchett',
    label: (
      <>
        <b>pratchett</b>: Cheeky, Sarcastic
      </>
    )
  },
  {
    id: 'gumshoe',
    label: (
      <>
        <b>gumshoe</b>: Hard-boiled Noir
      </>
    )
  },
  {
    id: 'hardyboys',
    label: (
      <>
        <b>hardyboys</b>: YA Mysteries
      </>
    )
  },
  {
    id: 'spaceopera',
    label: (
      <>
        <b>spaceopera</b>: Sci-fi Melodrama
      </>
    )
  },
  { id: 'original', label: 'Rewrite with Original Tone' },
  { id: 'none', label: '- No Rewrite -' }
]

export const LLMS = [
  { id: 'anthropic', label: 'Claude 3.5 Sonnet' },
  { id: 'hosted', label: 'Hosted' }
]

export const API_URL = 'https://manto--llm-text-adv-web-dev.modal.run'
