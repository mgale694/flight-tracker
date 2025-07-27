function Settings() {
  const [config, setConfig] = React.useState({
    address: '',
    search_radius_meters: 3000,
    max_flights: 20,
    max_elapsed_time: 1800,
  });
  const [loading, setLoading] = React.useState(true);
  const [saving, setSaving] = React.useState(false);
  const [message, setMessage] = React.useState('');

  React.useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const currentConfig = await window.FlightTrackerAPI.getConfig();
      setConfig(currentConfig);
    } catch (error) {
      console.error('Error loading config:', error);
      setMessage('Error loading configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    
    try {
      await window.FlightTrackerAPI.updateConfig(config);
      setMessage('Configuration saved successfully!');
    } catch (error) {
      console.error('Error saving config:', error);
      setMessage('Error saving configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  if (loading) {
    return React.createElement(
      'div',
      { className: 'settings-container' },
      React.createElement('div', { className: 'loading' }, 'Loading configuration...')
    );
  }

  return React.createElement(
    'div',
    { className: 'settings-container' },
    React.createElement('h1', null, 'Flight Tracker Settings'),
    React.createElement(
      'form',
      { onSubmit: handleSave, className: 'settings-form' },
      React.createElement(
        'div',
        { className: 'form-group' },
        React.createElement('label', { htmlFor: 'address' }, 'Address:'),
        React.createElement('input', {
          type: 'text',
          id: 'address',
          value: config.address,
          onChange: (e) => handleChange('address', e.target.value),
          placeholder: '31 Maltings Place, Fulham, London, SW62BU',
          required: true
        }),
        React.createElement('small', null, 'The address to center flight tracking around')
      ),
      React.createElement(
        'div',
        { className: 'form-group' },
        React.createElement('label', { htmlFor: 'radius' }, 'Search Radius (meters):'),
        React.createElement('input', {
          type: 'number',
          id: 'radius',
          value: config.search_radius_meters,
          onChange: (e) => handleChange('search_radius_meters', parseInt(e.target.value) || 3000),
          min: 1000,
          max: 10000,
          step: 500
        }),
        React.createElement('small', null, 'Radius in meters to search for flights around the address')
      ),
      React.createElement(
        'div',
        { className: 'form-group' },
        React.createElement('label', { htmlFor: 'maxFlights' }, 'Max Flights:'),
        React.createElement('input', {
          type: 'number',
          id: 'maxFlights',
          value: config.max_flights,
          onChange: (e) => handleChange('max_flights', parseInt(e.target.value) || 20),
          min: 1,
          max: 100
        }),
        React.createElement('small', null, 'Maximum number of flights to track in a session')
      ),
      React.createElement(
        'div',
        { className: 'form-group' },
        React.createElement('label', { htmlFor: 'maxTime' }, 'Max Session Time (seconds):'),
        React.createElement('input', {
          type: 'number',
          id: 'maxTime',
          value: config.max_elapsed_time,
          onChange: (e) => handleChange('max_elapsed_time', parseInt(e.target.value) || 1800),
          min: 300,
          max: 7200,
          step: 300
        }),
        React.createElement('small', null, 'Maximum session duration in seconds (default: 1800 = 30 minutes)')
      ),
      React.createElement(
        'div',
        { className: 'form-actions' },
        React.createElement(
          'button',
          { 
            type: 'submit', 
            disabled: saving, 
            className: 'save-button btn btn-primary'
          },
          saving ? 'Saving...' : 'Save Configuration'
        )
      ),
      message && React.createElement(
        'div',
        { className: `message ${message.includes('Error') ? 'error' : 'success'}` },
        message
      )
    )
  );
}

window.Settings = Settings;
