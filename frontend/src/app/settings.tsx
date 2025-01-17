export const GAMES = [
  { id: "905.z5", label: "9:05 by Adam Cadre" },
  { id: "lostpig.z8", label: "Lost Pig by Admiral Jota" },
  { id: "zork1.z5", label: "Zork I" },
];

export const TONES = [
  {
    id: "pratchett",
    label: (
      <>
        <b>pratchett</b>: cheeky, sarcastic
      </>
    ),
  },
  {
    id: "gumshoe",
    label: (
      <>
        <b>gumshoe</b>: hard-boiled noir
      </>
    ),
  },
  {
    id: "legal",
    label: (
      <>
        <b>legal</b>: formal, lawyer speak
      </>
    ),
  },
  {
    id: "spaceopera",
    label: (
      <>
        <b>spaceopera</b>: sci-fi melodrama
      </>
    ),
  },
  {
    id: "original",
    label: (
      <>
        <b>original</b>: keep original tone
      </>
    ),
  },
  { id: "none", label: "- no rewrite -" },
];

export const LLMS = [
  { id: "anthropic", label: "Claude 3.5 Sonnet" },
  { id: "openai", label: "GPT-4o-mini" },
  { id: "hosted", label: "Hosted" },
];

export const API_URL =
  `https://` +
  process.env.NEXT_PUBLIC_MODAL_USERNAME +
  "--llm-text-adv-web" +
  (process.env.NODE_ENV === "development" ? "-dev" : "") +
  ".modal.run";
