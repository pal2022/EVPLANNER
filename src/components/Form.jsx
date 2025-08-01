// import { useState, useCallback } from 'react';
// import axios from 'axios';
// import styles from './Form.module.css';

// export default function Form({ start, destination, onStartChange, onDestinationChange, mapUrls, setMapUrls, legendHtmls, setLegendHtmls, onClear, isFormMinimized, setIsFormMinimized }) {
//   const [formData, setFormData] = useState({
//     initial_soc: '',
//     threshold_soc: '',
//     ev_model: '',
//     consumption_rate: '',
//   });

//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState('');

//   const consumptionRates = {
//     "Tesla Model 3": 0.137,
//     "Mini Cooper SE": 0.149,
//     "Citroen e-C4 X": 0.157,
//     "Tesla Model Y Long Range AWD": 0.167,
//     "Porsche Taycan 4S Plus": 0.172,
//     "BMW i4 M50": 0.181,
//     "BMW i7 xDrive60": 0.199,
//     "Rolls-Royce Spectre": 0.219,
//     "VinFast VF 9 Extended Range": 0.239,
//     "Toyota PROACE Verso M 50 kWh": 0.257,
//     "Mercedes-Benz eVito Tourer Long 90 kWh": 0.281,
//     "Mercedes-Benz G 580": 0.322,
//     "Max": 4.0
//   };

//   const handleChange = useCallback((e) => {
//     const { name, value } = e.target;
//     if (name === 'ev_model') {
//       setFormData((prev) => ({
//         ...prev,
//         [name]: value,
//         consumption_rate: consumptionRates[value] || '',
//       }));
//     } else if (name === 'start') {
//       onStartChange(value);
//     } else if (name === 'destination') {
//       onDestinationChange(value);
//     } else {
//       setFormData((prev) => ({
//         ...prev,
//         [name]: value,
//       }));
//     }
//   }, [consumptionRates, onStartChange, onDestinationChange]);

//   const handleClear = useCallback(() => {
//     onStartChange('');
//     onDestinationChange('');
//     setFormData({
//       initial_soc: '',
//       threshold_soc: '',
//       ev_model: '',
//       consumption_rate: '',
//     });
//     setMapUrls([]);
//     setLegendHtmls([]);
//     setError('');
//     if (onClear) onClear();
//   }, [onStartChange, onDestinationChange, setMapUrls, setLegendHtmls, onClear]);

//   const handleSubmit = useCallback(async (e) => {
//     if (e) {
//       e.preventDefault();
//       e.stopPropagation();
//       if (e.stopImmediatePropagation) e.stopImmediatePropagation();
//     }
//     const { initial_soc, threshold_soc } = formData;
//     if (parseFloat(threshold_soc) > parseFloat(initial_soc)) {
//       alert("⚠️ Threshold battery percentage cannot be greater than Initial battery percentage.");
//       return;
//     }
//     try {
//       setLoading(true);
//       setError('');
//       setMapUrls([]);
//       setLegendHtmls([]);
//       const payload = {
//         start,
//         destination,
//         ...formData,
//       };
//       const response = await axios.post('http://localhost:5000/generate-route', payload);
//       const { success, map_urls, legend_htmls, error } = response.data;
//       if (success) {
//         setMapUrls(map_urls || []);
//         setLegendHtmls(legend_htmls || []);
//       } else {
//         setError(error || 'Something went wrong.');
//       }
//     } catch (err) {
//       setError('Failed to connect to the server.');
//     } finally {
//       setLoading(false);
//     }
//   }, [formData, start, destination, setMapUrls, setLegendHtmls]);

//   const handleGenerateClick = useCallback((e) => {
//     e.preventDefault();
//     e.stopPropagation();
//     handleSubmit();
//   }, [handleSubmit]);

//   const handleToggleForm = useCallback(() => {
//     setIsFormMinimized(prev => !prev);
//   }, [setIsFormMinimized]);

//   return (
//     <div className={`${styles.formContainer} w-full bg-white p-6 rounded-lg shadow`}>
//       {mapUrls && mapUrls.length > 0 && (
//         <button
//           onClick={handleToggleForm}
//           className="mb-4 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg shadow-lg transition-all duration-300 flex items-center justify-center border-0 text-xl"
//           title={isFormMinimized ? "Show Form" : "Hide Form"}
//         >
//           {isFormMinimized ? "👁️" : "👁️‍🗨️"}
//         </button>
//       )}
//       <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
//         <div className={`transition-all duration-300 ease-in-out ${
//           isFormMinimized ? 'hidden' : 'w-full max-w-sm'
//         }`}>
//           {!isFormMinimized && (
//             <div className={styles.form}>
//               <div className={styles.formTitle}>EV Route Planner Form</div>
//               <div className={styles.formGroup}>
//                 <label htmlFor="start">Starting Location:</label>
//                 <input
//                   type="text"
//                   id="start"
//                   name="start"
//                   required
//                   value={start}
//                   onChange={handleChange}
//                 />
//               </div>
//               <div className={styles.formGroup}>
//                 <label htmlFor="destination">Destination:</label>
//                 <input
//                   type="text"
//                   id="destination"
//                   name="destination"
//                   required
//                   value={destination}
//                   onChange={handleChange}
//                 />
//               </div>
//               <div className={styles.formGroup}>
//                 <label htmlFor="initial_soc">Initial Battery Percentage (%):</label>
//                 <input
//                   type="number"
//                   id="initial_soc"
//                   name="initial_soc"
//                   required
//                   min="0"
//                   max="100"
//                   step="0.1"
//                   value={formData.initial_soc}
//                   onChange={handleChange}
//                 />
//               </div>
//               <div className={styles.formGroup}>
//                 <label htmlFor="threshold_soc">Threshold Battery Percentage (%):</label>
//                 <input
//                   type="number"
//                   id="threshold_soc"
//                   name="threshold_soc"
//                   required
//                   min="0"
//                   max="50"
//                   step="0.1"
//                   value={formData.threshold_soc}
//                   onChange={handleChange}
//                 />
//               </div>
//               <div className={styles.formGroup}>
//                 <label htmlFor="ev_model">Select EV Model:</label>
//                 <select
//                   id="ev_model"
//                   name="ev_model"
//                   required
//                   value={formData.ev_model}
//                   onChange={handleChange}
//                 >
//                   <option value="" disabled>Select your EV</option>
//                   {Object.keys(consumptionRates).map((model) => (
//                     <option key={model} value={model}>{model}</option>
//                   ))}
//                 </select>
//                 <input type="hidden" name="consumption_rate" value={formData.consumption_rate} />
//               </div>
//               <div className={styles.buttonRow}>
//                 <button
//                   type="button"
//                   onClick={handleClear}
//                   className={styles.clearButton}
//                 >
//                   Clear Form
//                 </button>
//                 <button
//                   type="button"
//                   onClick={handleGenerateClick}
//                   className={styles.generateButton}
//                   disabled={loading}
//                 >
//                   {loading ? 'Generating...' : 'Generate Route'}
//                 </button>
//               </div>
//             </div>
//           )}
//           {loading && <div className={styles.loading}>🛠️ Generating map... Please wait.</div>}
//           {error && <div className={styles.error}>{error}</div>}
//         </div>
//       </div>
//     </div>
//   );
// }



import { useState, useCallback } from 'react';
import axios from 'axios';
import styles from './Form.module.css';

export default function Form({ start, destination, onStartChange, onDestinationChange, mapUrls, setMapUrls, legendHtmls, setLegendHtmls, onClear, isFormMinimized, setIsFormMinimized }) {
  const [formData, setFormData] = useState({
    initial_soc: '',
    threshold_soc: '',
    ev_model: '',
    consumption_rate: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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
    if (name === 'ev_model') {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
        consumption_rate: consumptionRates[value] || '',
      }));
    } else if (name === 'start') {
      onStartChange(value);
    } else if (name === 'destination') {
      onDestinationChange(value);
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  }, [consumptionRates, onStartChange, onDestinationChange]);

  const handleClear = useCallback(() => {
    onStartChange('');
    onDestinationChange('');
    setFormData({
      initial_soc: '',
      threshold_soc: '',
      ev_model: '',
      consumption_rate: '',
    });
    setMapUrls([]);
    setLegendHtmls([]);
    setError('');
    if (onClear) onClear();
  }, [onStartChange, onDestinationChange, setMapUrls, setLegendHtmls, onClear]);

  const handleSubmit = useCallback(async (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
      if (e.stopImmediatePropagation) e.stopImmediatePropagation();
    }
    const { initial_soc, threshold_soc } = formData;
    if (parseFloat(threshold_soc) > parseFloat(initial_soc)) {
      alert("⚠️ Threshold battery percentage cannot be greater than Initial battery percentage.");
      return;
    }
    try {
      setLoading(true);
      setError('');
      setMapUrls([]);
      setLegendHtmls([]);
      const payload = {
        start,
        destination,
        ...formData,
      };
      const response = await axios.post(`https://evplanner-1.onrender.com/generate-route`, payload);
      const { success, map_urls, legend_htmls, error } = response.data;
      if (success) {
        setMapUrls(map_urls || []);
        setLegendHtmls(legend_htmls || []);
      } else {
        setError(error || 'Something went wrong.');
      }
    } catch (err) {
      setError('Failed to connect to the server.');
    } finally {
      setLoading(false);
    }
  }, [formData, start, destination, setMapUrls, setLegendHtmls]);

  const handleGenerateClick = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    handleSubmit();
  }, [handleSubmit]);

  const handleToggleForm = useCallback(() => {
    setIsFormMinimized(prev => !prev);
  }, [setIsFormMinimized]);

  return (
    <div className={`${styles.formContainer} w-full bg-white p-6 rounded-lg shadow`}>
      {mapUrls && mapUrls.length > 0 && (
        <button
          onClick={handleToggleForm}
          className="mb-4 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg shadow-lg transition-all duration-300 flex items-center justify-center border-0 text-xl"
          title={isFormMinimized ? "Show Form" : "Hide Form"}
        >
          {isFormMinimized ? "👁️" : "👁️‍🗨️"}
        </button>
      )}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
        <div className={`transition-all duration-300 ease-in-out ${
          isFormMinimized ? 'hidden' : 'w-full max-w-sm'
        }`}>
          {!isFormMinimized && (
            <div className={styles.form}>
              <div className={styles.formTitle}>EV Route Planner Form</div>
              <div className={styles.formGroup}>
                <label htmlFor="start">Starting Location:</label>
                <input
                  type="text"
                  id="start"
                  name="start"
                  required
                  value={start}
                  onChange={handleChange}
                />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="destination">Destination:</label>
                <input
                  type="text"
                  id="destination"
                  name="destination"
                  required
                  value={destination}
                  onChange={handleChange}
                />
              </div>
              <div className={styles.formGroup}>
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
              </div>
              <div className={styles.formGroup}>
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
              </div>
              <div className={styles.formGroup}>
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
              </div>
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
          )}
          {loading && <div className={styles.loading}>🛠️ Generating map... Please wait.</div>}
          {error && <div className={styles.error}>{error}</div>}
        </div>
      </div>
    </div>
  );
}
