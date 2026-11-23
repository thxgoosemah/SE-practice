import type { Room } from "../types";

interface RoomSelectorProps {
  rooms: Room[];
  selectedId: string;
  onSelect: (id: string) => void;
}

export function RoomSelector({ rooms, selectedId, onSelect }: RoomSelectorProps) {
  return (
    <select
      className="room-select"
      value={selectedId}
      onChange={(e) => onSelect(e.target.value)}
      aria-label="Select a room"
    >
      {rooms.map((room) => (
        <option key={room.id} value={room.id}>
          {room.name} — {room.building}, Floor {room.floor}
          {room.blocked ? " (Blocked)" : ""}
        </option>
      ))}
    </select>
  );
}
