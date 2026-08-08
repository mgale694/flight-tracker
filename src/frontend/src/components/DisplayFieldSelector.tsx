/** Touch-friendly e-paper field selection and ordering. */

import './DisplayFieldSelector.css';

interface FieldOption {
  id: string;
  label: string;
  category: string;
}

interface DisplayFieldSelectorProps {
  selectedFields: string[];
  onChange: (fields: string[]) => void;
}

const AVAILABLE_FIELDS: FieldOption[] = [
  { id: 'FROM', label: 'From · full airport name', category: 'Recommended' },
  { id: 'TO', label: 'To · full airport name', category: 'Recommended' },
  { id: 'AIRLINE', label: 'Airline', category: 'Recommended' },
  { id: 'MODEL', label: 'Aircraft model', category: 'Recommended' },
  { id: 'REG', label: 'Registration', category: 'Recommended' },
  { id: 'ROUTE', label: 'Route codes', category: 'Recommended' },
  { id: 'callsign', label: 'Callsign', category: 'Flight' },
  { id: 'registration', label: 'Registration', category: 'Flight' },
  { id: 'altitude', label: 'Altitude', category: 'Flight' },
  { id: 'speed', label: 'Speed', category: 'Flight' },
  { id: 'heading', label: 'Heading', category: 'Flight' },
  { id: 'aircraft', label: 'Aircraft', category: 'Aircraft' },
  { id: 'airline', label: 'Airline', category: 'Airline' },
  { id: 'origin_name', label: 'Origin airport name', category: 'Airports' },
  { id: 'destination_name', label: 'Destination airport name', category: 'Airports' },
  { id: 'distance', label: 'Distance', category: 'Position' },
  { id: 'latitude', label: 'Latitude', category: 'Position' },
  { id: 'longitude', label: 'Longitude', category: 'Position' },
];

function fieldLabel(fieldId: string): string {
  return AVAILABLE_FIELDS.find((field) => field.id === fieldId)?.label ?? fieldId;
}

function FieldOptions({ excluded, current }: { excluded: string[]; current?: string }) {
  const categories = [...new Set(AVAILABLE_FIELDS.map((field) => field.category))];
  const legacyCurrent = current && !AVAILABLE_FIELDS.some((field) => field.id === current);
  return (
    <>
      {legacyCurrent && <option value={current}>{current}</option>}
      {categories.map((category) => (
        <optgroup label={category} key={category}>
          {AVAILABLE_FIELDS.filter(
            (field) => field.category === category && (!excluded.includes(field.id) || field.id === current),
          ).map((field) => (
            <option value={field.id} key={field.id}>{field.label}</option>
          ))}
        </optgroup>
      ))}
    </>
  );
}

export default function DisplayFieldSelector({
  selectedFields,
  onChange,
}: DisplayFieldSelectorProps) {
  const replaceField = (index: number, fieldId: string) => {
    const next = [...selectedFields];
    next[index] = fieldId;
    onChange(next);
  };

  const moveField = (index: number, offset: number) => {
    const destination = index + offset;
    if (destination < 0 || destination >= selectedFields.length) return;
    const next = [...selectedFields];
    [next[index], next[destination]] = [next[destination], next[index]];
    onChange(next);
  };

  const removeField = (index: number) => {
    onChange(selectedFields.filter((_, fieldIndex) => fieldIndex !== index));
  };

  const addField = (fieldId: string) => {
    if (fieldId && selectedFields.length < 5) onChange([...selectedFields, fieldId]);
  };

  return (
    <div className="display-field-selector">
      <p className="field-selector-hint">
        Line 1 appears at the top. Use the native dropdowns and arrow buttons on any device.
      </p>

      <ol className="selected-field-list">
        {selectedFields.map((fieldId, index) => (
          <li className="selected-field-row" key={`${fieldId}-${index}`}>
            <span className="field-number" aria-hidden="true">{index + 1}</span>
            <label>
              <span className="visually-hidden">E-paper line {index + 1}</span>
              <select
                value={fieldId}
                onChange={(event) => replaceField(index, event.target.value)}
                aria-label={`E-paper line ${index + 1}: ${fieldLabel(fieldId)}`}
              >
                <FieldOptions excluded={selectedFields} current={fieldId} />
              </select>
            </label>
            <div className="field-order-actions">
              <button
                type="button"
                onClick={() => moveField(index, -1)}
                disabled={index === 0}
                aria-label={`Move ${fieldLabel(fieldId)} up`}
              >↑</button>
              <button
                type="button"
                onClick={() => moveField(index, 1)}
                disabled={index === selectedFields.length - 1}
                aria-label={`Move ${fieldLabel(fieldId)} down`}
              >↓</button>
              <button
                type="button"
                className="remove-field"
                onClick={() => removeField(index)}
                aria-label={`Remove ${fieldLabel(fieldId)}`}
              >×</button>
            </div>
          </li>
        ))}
      </ol>

      {selectedFields.length < 5 && (
        <label className="add-field-control">
          <span>Add another line</span>
          <select value="" onChange={(event) => addField(event.target.value)}>
            <option value="">Choose a field…</option>
            <FieldOptions excluded={selectedFields} />
          </select>
        </label>
      )}
      <span className="field-count">{selectedFields.length} of 5 lines selected</span>
    </div>
  );
}
