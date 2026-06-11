import type { DragEvent, ReactNode } from "react";

import { encodeStageDragPayload, REACT_FLOW_DRAG_MIME } from "./builderDnD";

type DraggableAssetChipProps = {
  stageId: string;
  testId: string;
  onClick?: () => void;
  children: ReactNode;
  className?: string;
};

export function DraggableAssetChip({
  stageId,
  testId,
  onClick,
  children,
  className,
}: DraggableAssetChipProps) {
  const onDragStart = (event: DragEvent<HTMLButtonElement>) => {
    event.dataTransfer.setData(REACT_FLOW_DRAG_MIME, encodeStageDragPayload(stageId));
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <button
      type="button"
      draggable
      data-testid={testId}
      className={className}
      onDragStart={onDragStart}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
