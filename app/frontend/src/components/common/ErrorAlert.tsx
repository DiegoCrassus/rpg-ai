export function ErrorAlert({ message }: { message: string }) {
  return (
    <div className="rounded-md border border-red-800 bg-red-950/50 px-4 py-3 text-sm text-red-200">
      {message}
    </div>
  );
}
