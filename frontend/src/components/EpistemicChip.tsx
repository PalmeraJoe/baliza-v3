type Props = {
  kind:
    | 'FACT'
    | 'EXTERNAL INDICATOR'
    | 'DERIVED INDICATOR'
    | 'CONTEXT ONLY'
    | 'DATA GAP'
    | 'UNCERTAINTY'
    | 'RECOMMENDATION'
    | 'DECISION'
    | 'DEMO / NON-SCIENTIFIC'
    | 'REAL SCIENTIFIC DATA'
    | string
}

export function EpistemicChip({ kind }: Props) {
  const cls =
    kind.includes('DEMO')
      ? 'chip-demo'
      : kind.includes('GAP')
        ? 'chip-gap'
        : kind.includes('EXTERNAL')
          ? 'chip-ext'
          : kind.includes('CONTEXT')
            ? 'chip-ctx'
            : kind.includes('RECOMMENDATION')
              ? 'chip-rec'
              : kind.includes('DECISION')
                ? 'chip-dec'
                : kind.includes('REAL')
                  ? 'chip-real'
                  : kind.includes('ALERT') || kind.includes('WARNING')
                    ? 'chip-alert'
                    : 'chip-ext'
  return (
    <span className={`chip ${cls}`} data-testid={`chip-${kind}`}>
      {kind}
    </span>
  )
}
