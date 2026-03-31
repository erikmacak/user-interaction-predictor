const TIME_UNITS = {
  HOURS_IN_SECONDS: 3600,
  MINUTES_IN_SECONDS: 60,
  PAD_LENGTH: 2,
  PAD_CHAR: '0',
} as const;

export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / TIME_UNITS.HOURS_IN_SECONDS);
  const minutes = Math.floor(
    (seconds % TIME_UNITS.HOURS_IN_SECONDS) / TIME_UNITS.MINUTES_IN_SECONDS
  );
  const secs = seconds % TIME_UNITS.MINUTES_IN_SECONDS;

  return [hours, minutes, secs]
    .map((value) => String(value).padStart(TIME_UNITS.PAD_LENGTH, TIME_UNITS.PAD_CHAR))
    .join(':');
}