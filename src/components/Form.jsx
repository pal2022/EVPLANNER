import { useState, useCallback } from 'react';
import axios from 'axios';
import styles from './Form.module.css';

export default function Form() {
  const [formData, setFormData] = useState({
    start: '',
    destination: '',
    initial_soc: '',
    threshold_soc: '',
    ev_model: '',
    consumption_rate: '',
  });

  const [loading, setLoading] = useState(false);
  const [mapUrls, setMapUrls] = useState([]);
  const [legendHtmls, setLegendHtmls] = useState([]);
  const [error, setError] = useState('');
  const [isFormMinimized, setIsFormMinimized] = useState(false);

  const consumptionRates = {
    "Tesla Model 3": 0.137,
    "Mini Cooper SE": 0.149,
    "Citroen e-C4 X": 0.157,
    "Tesla Model Y Long Range AWD": 0.167,
    "Porsche Taycan 4S Plus": 0.172,
    "BMW i4 M50": 0.181,
    "BMW i7 xDrive60": 0.199,
    "Rolls-Royce Spectre": 0.219,
    "VinFast VF 9 Extended Range": 0.239,
    "Toyota PROACE Verso M 50 kWh": 0.257,
    "Mercedes-Benz eVito Tourer Long 90 kWh": 0.281,
    "Mercedes-Benz G 580": 0.322,
    "Max": 4.0
  };

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    console.log('Form field changed:', name, value);

    if (name === 'ev_model') {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
        consumption_rate: consumptionRates[value] || '',
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  }, [consumptionRates]);

  const handleClear = useCallback(() => {
    console.log('Clearing form');
    setFormData({
      start: '',
      destination: '',
      initial_soc: '',
      threshold_soc: '',
      ev_model: '',
      consumption_rate: '',
    });
    setMapUrls([]);
    setLegendHtmls([]);
    setError('');
  }, []);

  const handleSubmit = useCallback(async (e) => {
    console.log('Form submit event triggered');
    
    // Prevent any default behavior
    if (e) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
    }
    
    console.log('Form submission prevented, proceeding with API call');
    
    const { initial_soc, threshold_soc } = formData;

    if (parseFloat(threshold_soc) > parseFloat(initial_soc)) {
      alert("⚠️ Threshold battery percentage cannot be greater than Initial battery percentage.");
      return;
    }

    try {
      console.log('Setting loading state');
      setLoading(true);
      setError('');
      setMapUrls([]);
      setLegendHtmls([]);

      console.log('Submitting form data:', formData);

      const response = await axios.post('http://localhost:5000/generate-route', formData);
      console.log('Response received:', response.data);
      
      const { success, map_urls, legend_htmls, error } = response.data;

      if (success) {
        console.log('Setting map URLs:', map_urls);
        console.log('Setting legend HTMLs:', legend_htmls);
        setMapUrls(map_urls || []);
        setLegendHtmls(legend_htmls || []);
      } else {
        setError(error || 'Something went wrong.');
      }
    } catch (err) {
      console.error('Error during form submission:', err);
      setError('Failed to connect to the server.');
    } finally {
      console.log('Setting loading to false');
      setLoading(false);
    }
  }, [formData]);

  const handleGenerateClick = useCallback((e) => {
    console.log('Generate button clicked');
    e.preventDefault();
    e.stopPropagation();
    handleSubmit();
  }, [handleSubmit]);

  const handleToggleForm = useCallback(() => {
    setIsFormMinimized(prev => !prev);
  }, []);

  console.log('Form component rendered with state:', { 
    loading, 
    mapUrls: mapUrls.length, 
    legendHtmls: legendHtmls.length, 
    error 
  });

  return (
    <div className={styles.formContainer}>
      {/* Toggle Button - Always visible when maps are generated */}
      {mapUrls && mapUrls.length > 0 && (
        <button
          onClick={handleToggleForm}
          className="mb-4 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg shadow-lg transition-all duration-300 flex items-center justify-center border-0 text-xl"
          title={isFormMinimized ? "Show Form" : "Hide Form"}
        >
          {isFormMinimized ? "👁️" : "👁️‍🗨️"}
        </button>
      )}

      <div className="flex gap-8">
        {/* Form Section - Conditional width based on minimized state */}
        <div className={`transition-all duration-300 ease-in-out ${
          isFormMinimized ? 'hidden' : 'w-1/4 min-w-0'
        }`}>
          <div className={styles.form}>
            <label htmlFor="start">Starting Location:</label>
            <input 
              type="text" 
              id="start" 
              name="start" 
              required 
              value={formData.start} 
              onChange={handleChange} 
            />

            <label htmlFor="destination">Destination:</label>
            <input 
              type="text" 
              id="destination" 
              name="destination" 
              required 
              value={formData.destination} 
              onChange={handleChange} 
            />

            <label htmlFor="initial_soc">Initial Battery Percentage (%):</label>
            <input 
              type="number" 
              id="initial_soc" 
              name="initial_soc" 
              required 
              min="0" 
              max="100" 
              step="0.1" 
              value={formData.initial_soc} 
              onChange={handleChange} 
            />

            <label htmlFor="threshold_soc">Threshold Battery Percentage (%):</label>
            <input 
              type="number" 
              id="threshold_soc" 
              name="threshold_soc" 
              required 
              min="0" 
              max="50" 
              step="0.1" 
              value={formData.threshold_soc} 
              onChange={handleChange} 
            />

            <label htmlFor="ev_model">Select EV Model:</label>
            <select 
              id="ev_model" 
              name="ev_model" 
              required 
              value={formData.ev_model} 
              onChange={handleChange}
            >
              <option value="" disabled>Select your EV</option>
              {Object.keys(consumptionRates).map((model) => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>

            <input type="hidden" name="consumption_rate" value={formData.consumption_rate} />

            <div className={styles.buttonRow}>
              <button 
                type="button" 
                onClick={handleClear} 
                className={styles.clearButton}
              >
                Clear Form
              </button>
              <button 
                type="button" 
                onClick={handleGenerateClick}
                className={styles.generateButton}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Route'}
              </button>
            </div>
          </div>

          {loading && <div className={styles.loading}>🛠️ Generating map... Please wait.</div>}

          {error && <div className={styles.error}>{error}</div>}
        </div>

        {/* Spacer - Conditional width based on minimized state */}
        <div className={`transition-all duration-300 ease-in-out ${
          isFormMinimized ? 'hidden' : 'w-[5%]'
        }`}></div>

        {/* Maps and Legends Section - Conditional width based on minimized state */}
        {mapUrls && mapUrls.length > 0 && (
          <div className={`transition-all duration-300 ease-in-out flex gap-6 ${
            isFormMinimized ? 'w-full' : 'w-[70%]'
          }`}>
            {/* Map Section - Conditional width based on minimized state */}
            <div className={`transition-all duration-300 ease-in-out space-y-4 min-w-0 ${
              isFormMinimized ? 'w-[80%]' : 'w-[75%]'
            }`}>
              {mapUrls.map((url, idx) => (
                <div key={`map-${idx}-${url}`} className="border border-gray-200 rounded-lg shadow-md p-4 bg-white">
                  {/* <h3 className="text-md font-semibold text-gray-700 mb-2">Route {idx + 1}</h3> */}
                  
                  {/* Debug Info
                  <div className="text-xs text-gray-500 mb-2">
                    Map URL: {url}
                  </div> */}

                  {/* Map Display */}
                  <iframe
                    src={url}
                    title={`Route ${idx + 1}`}
                    className="w-full h-[600px] rounded-lg border"
                    loading="lazy"
                    onError={(e) => console.error('Iframe failed to load:', e)}
                    onLoad={() => console.log('Iframe loaded successfully for route:', idx + 1)}
                  ></iframe>
                  
                  {/* Fallback if iframe fails
                  <div className="mt-2 text-sm text-gray-600">
                    <a href={url} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">
                      Open map in new tab if not displaying above
                    </a>
                  </div> */}
                </div>
              ))}
            </div>

            {/* Legend Section - Keep the same size */}
            <div className="w-[20%] space-y-4 min-w-0">
              {legendHtmls && legendHtmls.map((legend, idx) => (
                <div key={`legend-${idx}`} className="p-3">
                  <div
                    className="text-xs text-gray-700 overflow-auto max-h-[400px]"
                    dangerouslySetInnerHTML={{ __html: legend }}
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
