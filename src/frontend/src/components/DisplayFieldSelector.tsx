/**
 * Display Field Selector - Drag and drop interface for e-ink display fields
 */

import { useState } from 'react';
import './DisplayFieldSelector.css';

interface FieldOption {
  id: string;
  label: string;
  description: string;
  category: string;
}

interface DisplayFieldSelectorProps {
  selectedFields: string[];
  onChange: (fields: string[]) => void;
}

const AVAILABLE_FIELDS: FieldOption[] = [
  // Basic Identification
  { id: 'id', label: 'Flight ID', description: 'Unique flight identifier', category: 'Basic' },
  { id: 'icao_24bit', label: 'ICAO 24-bit', description: 'Aircraft ICAO 24-bit address', category: 'Basic' },
  { id: 'callsign', label: 'Callsign', description: 'Flight callsign', category: 'Basic' },
  { id: 'number', label: 'Flight Number', description: 'Flight number', category: 'Basic' },
  { id: 'registration', label: 'Registration', description: 'Aircraft registration', category: 'Basic' },
  
  // Aircraft Information
  { id: 'aircraft', label: 'Aircraft', description: 'Aircraft model/code', category: 'Aircraft' },
  { id: 'aircraft_code', label: 'Aircraft Code', description: 'ICAO aircraft type code', category: 'Aircraft' },
  { id: 'aircraft_model', label: 'Aircraft Model', description: 'Full aircraft model name', category: 'Aircraft' },
  { id: 'aircraft_age', label: 'Aircraft Age', description: 'Age of aircraft', category: 'Aircraft' },
  
  // Airline Information
  { id: 'airline', label: 'Airline', description: 'Airline name', category: 'Airline' },
  { id: 'airline_name', label: 'Airline Name', description: 'Full airline name', category: 'Airline' },
  { id: 'airline_short_name', label: 'Airline Short', description: 'Short airline name', category: 'Airline' },
  { id: 'airline_iata', label: 'Airline IATA', description: 'Airline IATA code', category: 'Airline' },
  { id: 'airline_icao', label: 'Airline ICAO', description: 'Airline ICAO code', category: 'Airline' },
  
  // Origin Airport
  { id: 'origin', label: 'Origin Code', description: 'Origin airport IATA code', category: 'Origin' },
  { id: 'origin_name', label: 'Origin Name', description: 'Origin airport name with code', category: 'Origin' },
  { id: 'origin_airport_icao', label: 'Origin ICAO', description: 'Origin airport ICAO code', category: 'Origin' },
  { id: 'origin_airport_country_name', label: 'Origin Country', description: 'Origin country name', category: 'Origin' },
  { id: 'origin_airport_gate', label: 'Origin Gate', description: 'Departure gate', category: 'Origin' },
  { id: 'origin_airport_terminal', label: 'Origin Terminal', description: 'Departure terminal', category: 'Origin' },
  
  // Destination Airport
  { id: 'destination', label: 'Dest Code', description: 'Destination airport IATA code', category: 'Destination' },
  { id: 'destination_name', label: 'Dest Name', description: 'Destination airport name with code', category: 'Destination' },
  { id: 'destination_airport_icao', label: 'Dest ICAO', description: 'Destination airport ICAO code', category: 'Destination' },
  { id: 'destination_airport_country_name', label: 'Dest Country', description: 'Destination country name', category: 'Destination' },
  { id: 'destination_airport_gate', label: 'Dest Gate', description: 'Arrival gate', category: 'Destination' },
  { id: 'destination_airport_terminal', label: 'Dest Terminal', description: 'Arrival terminal', category: 'Destination' },
  { id: 'destination_airport_baggage', label: 'Baggage Claim', description: 'Baggage claim area', category: 'Destination' },
  
  // Flight Status
  { id: 'altitude', label: 'Altitude', description: 'Current altitude in feet', category: 'Status' },
  { id: 'speed', label: 'Speed', description: 'Ground speed in knots', category: 'Status' },
  { id: 'heading', label: 'Heading', description: 'Aircraft heading in degrees', category: 'Status' },
  { id: 'vertical_speed', label: 'Vertical Speed', description: 'Climb/descent rate', category: 'Status' },
  { id: 'squawk', label: 'Squawk', description: 'Transponder code', category: 'Status' },
  { id: 'on_ground', label: 'On Ground', description: 'Ground status', category: 'Status' },
  { id: 'status_text', label: 'Status', description: 'Flight status text', category: 'Status' },
  
  // Position & Distance
  { id: 'distance', label: 'Distance', description: 'Distance from tracking point', category: 'Position' },
  { id: 'latitude', label: 'Latitude', description: 'Current latitude', category: 'Position' },
  { id: 'longitude', label: 'Longitude', description: 'Current longitude', category: 'Position' },
];

export default function DisplayFieldSelector({ selectedFields, onChange }: DisplayFieldSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [draggedField, setDraggedField] = useState<string | null>(null);

  const filteredFields = AVAILABLE_FIELDS.filter(field => 
    !selectedFields.includes(field.id) &&
    (field.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
     field.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
     field.category.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const groupedFields = filteredFields.reduce((acc, field) => {
    if (!acc[field.category]) {
      acc[field.category] = [];
    }
    acc[field.category].push(field);
    return acc;
  }, {} as Record<string, FieldOption[]>);

  const handleDragStart = (e: React.DragEvent, index: number) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const newFields = [...selectedFields];
    const draggedItem = newFields[draggedIndex];
    newFields.splice(draggedIndex, 1);
    newFields.splice(index, 0, draggedItem);
    
    onChange(newFields);
    setDraggedIndex(index);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDraggedIndex(null);
    setDraggedField(null);
  };

  const handleFieldDragStart = (e: React.DragEvent, fieldId: string) => {
    setDraggedField(fieldId);
    e.dataTransfer.effectAllowed = 'copy';
  };

  const handleFieldDrop = (e: React.DragEvent, index?: number) => {
    e.preventDefault();
    if (!draggedField) return;
    
    if (selectedFields.length >= 5) {
      alert('Maximum 5 fields allowed');
      setDraggedField(null);
      return;
    }

    const newFields = [...selectedFields];
    if (index !== undefined) {
      newFields.splice(index, 0, draggedField);
    } else {
      newFields.push(draggedField);
    }
    onChange(newFields);
    setDraggedField(null);
  };

  const removeField = (index: number) => {
    const newFields = selectedFields.filter((_, i) => i !== index);
    onChange(newFields);
  };

  const getFieldLabel = (fieldId: string) => {
    const field = AVAILABLE_FIELDS.find(f => f.id === fieldId);
    return field ? field.label : fieldId;
  };

  return (
    <div className="display-field-selector">
      <div className="selector-section">
        <h4>Selected Fields (Drag to Reorder)</h4>
        <p className="hint">Choose up to 5 fields • Drag to reorder • Click ✕ to remove</p>
        
        <div 
          className="selected-fields"
          onDragOver={(e) => {
            e.preventDefault();
            if (draggedField && selectedFields.length < 5) {
              e.currentTarget.classList.add('drag-over');
            }
          }}
          onDragLeave={(e) => {
            e.currentTarget.classList.remove('drag-over');
          }}
          onDrop={(e) => handleFieldDrop(e)}
        >
          {selectedFields.length === 0 ? (
            <div className="empty-state">
              <p>No fields selected</p>
              <p className="empty-hint">Drag fields from below or use defaults</p>
            </div>
          ) : (
            selectedFields.map((fieldId, index) => (
              <div
                key={fieldId}
                className={`selected-field ${draggedIndex === index ? 'dragging' : ''}`}
                draggable
                onDragStart={(e) => handleDragStart(e, index)}
                onDragOver={(e) => handleDragOver(e, index)}
                onDragEnd={handleDrop}
              >
                <span className="field-number">{index + 1}</span>
                <span className="field-label">{getFieldLabel(fieldId)}</span>
                <button
                  type="button"
                  className="remove-btn"
                  onClick={() => removeField(index)}
                  aria-label={`Remove ${getFieldLabel(fieldId)}`}
                >
                  ✕
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="selector-section">
        <h4>Available Fields</h4>
        <input
          type="text"
          className="search-input"
          placeholder="Search fields..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />

        <div className="available-fields">
          {Object.keys(groupedFields).length === 0 ? (
            <p className="no-results">No fields found matching "{searchQuery}"</p>
          ) : (
            Object.entries(groupedFields).map(([category, fields]) => (
              <div key={category} className="field-category">
                <h5>{category}</h5>
                <div className="field-list">
                  {fields.map(field => (
                    <div
                      key={field.id}
                      className="available-field"
                      draggable
                      onDragStart={(e) => handleFieldDragStart(e, field.id)}
                    >
                      <div className="field-info">
                        <span className="field-label">{field.label}</span>
                        <span className="field-description">{field.description}</span>
                      </div>
                      <span className="drag-handle">⋮⋮</span>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
