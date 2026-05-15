/** Strip a leading "Dr. " prefix so the caller can add it consistently. */
export function doctorName(name: string): string {
  return name.replace(/^Dr\.\s*/i, "");
}
