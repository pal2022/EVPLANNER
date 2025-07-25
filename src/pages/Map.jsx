// import React, { useState } from 'react';
// import Form from '../components/Form';
// import MapSelector from '../components/MapSelector';

// export default function Map() {
//   const [start, setStart] = useState('');
//   const [destination, setDestination] = useState('');
//   const [mapUrls, setMapUrls] = useState([]);
//   const [legendHtmls, setLegendHtmls] = useState([]);
//   const [isFormMinimized, setIsFormMinimized] = useState(false);

//   const handleClear = () => {
//     setMapUrls([]);
//     setLegendHtmls([]);
//     setStart('');
//     setDestination('');
//     setIsFormMinimized(false);
//   };

//   const showMapSelector = mapUrls.length === 0;

//   return (
//     <section>
//       <h2 className="text-3xl font-semibold text-center text-blue-700 mb-8">
//         Plan Your EV Route
//       </h2>
//       <div style={{ display: 'flex', flexDirection: 'row', gap: '2rem', alignItems: 'flex-start', width: '100%' }}>
//         {(!isFormMinimized || showMapSelector) && (
//           <div style={{ flex: showMapSelector ? '0 0 400px' : 1, minWidth: showMapSelector ? '350px' : '0', display: 'flex', alignItems: 'center', minHeight: '500px', width: showMapSelector ? undefined : '100%' }}>
//             <Form
//               start={start}
//               destination={destination}
//               onStartChange={setStart}
//               onDestinationChange={setDestination}
//               mapUrls={mapUrls}
//               setMapUrls={setMapUrls}
//               legendHtmls={legendHtmls}
//               setLegendHtmls={setLegendHtmls}
//               onClear={handleClear}
//               isFormMinimized={isFormMinimized}
//               setIsFormMinimized={setIsFormMinimized}
//             />
//           </div>
//         )}
//         {showMapSelector ? (
//           <div style={{ flex: 1, minWidth: '400px', minHeight: '500px' }}>
//             <MapSelector
//               start={start}
//               destination={destination}
//               onStartChange={setStart}
//               onDestinationChange={setDestination}
//             />
//           </div>
//         ) : (
//           <div style={{ flex: isFormMinimized ? 1 : 2, minWidth: '400px', minHeight: '500px', display: 'flex', gap: '2rem', width: isFormMinimized ? '100%' : undefined }}>
//             <div style={{ flex: 3, minWidth: 0 }}>
//               {mapUrls.map((url, idx) => (
//                 <div key={`map-${idx}-${url}`} style={{ border: '1px solid #e5e7eb', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0,0,0,0.08)', marginBottom: '1.5rem', background: '#fff', padding: '1rem' }}>
//                   <iframe
//                     src={url}
//                     title={`Route ${idx + 1}`}
//                     style={{ width: '100%', height: '600px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
//                     loading="lazy"
//                   ></iframe>
//                 </div>
//               ))}
//             </div>
//             <div style={{ flex: 1, minWidth: 0 }}>
//               {legendHtmls && legendHtmls.map((legend, idx) => (
//                 <div key={`legend-${idx}`} style={{ background: '#f9fafb', borderRadius: '8px', padding: '1rem', marginBottom: '1rem', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
//                   <div
//                     style={{ fontSize: '0.95rem', color: '#374151', overflow: 'auto', maxHeight: '400px' }}
//                     dangerouslySetInnerHTML={{ __html: legend }}
//                   />
//                 </div>
//               ))}
//             </div>
//           </div>
//         )}
//       </div>
//     </section>
//   );
// }


import React, { useState } from 'react';
import Form from '../components/Form';
import MapSelector from '../components/MapSelector';

export default function Map() {
  const [start, setStart] = useState('');
  const [destination, setDestination] = useState('');
  const [mapUrls, setMapUrls] = useState([]);
  const [legendHtmls, setLegendHtmls] = useState([]);
  const [isFormMinimized, setIsFormMinimized] = useState(false);

  const handleClear = () => {
    setMapUrls([]);
    setLegendHtmls([]);
    setStart('');
    setDestination('');
    setIsFormMinimized(false);
  };

  const showMapSelector = mapUrls.length === 0;

  return (
    <section>
      <h2 className="text-3xl font-semibold text-center text-blue-700 mb-8">
        Plan Your EV Route
      </h2>
      <div style={{ position: 'relative', display: 'flex', flexDirection: 'row', gap: '2rem', alignItems: 'flex-start', width: '100%' }}>
        {(!isFormMinimized || showMapSelector) && (
          <div style={{ flex: showMapSelector ? '0 0 400px' : 1, minWidth: showMapSelector ? '350px' : '0', display: 'flex', alignItems: 'center', minHeight: '500px', width: showMapSelector ? undefined : '100%' }}>
            <Form
              start={start}
              destination={destination}
              onStartChange={setStart}
              onDestinationChange={setDestination}
              mapUrls={mapUrls}
              setMapUrls={setMapUrls}
              legendHtmls={legendHtmls}
              setLegendHtmls={setLegendHtmls}
              onClear={handleClear}
              isFormMinimized={isFormMinimized}
              setIsFormMinimized={setIsFormMinimized}
            />
          </div>
        )}

        {/* Restore Form Icon when minimized */}
        {isFormMinimized && !showMapSelector && (
          <button
            onClick={() => setIsFormMinimized(false)}
            style={{
              position: 'absolute',
              top: '5rem',
              left: '1rem',
              background: '#2563eb',
              color: '#fff',
              padding: '0.5rem 0.75rem',
              borderRadius: '50%',
              boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
              zIndex: 1000,
              cursor: 'pointer',
            }}
            title="Show Form"
          >
            &#x21F1;
          </button>
        )}

        {showMapSelector ? (
          <div style={{ flex: 1, minWidth: '400px', minHeight: '500px' }}>
            <MapSelector
              start={start}
              destination={destination}
              onStartChange={setStart}
              onDestinationChange={setDestination}
            />
          </div>
        ) : (
          <div style={{ flex: isFormMinimized ? 1 : 2, minWidth: '400px', minHeight: '500px', display: 'flex', gap: '2rem', width: isFormMinimized ? '100%' : undefined }}>
            <div style={{ flex: 3, minWidth: 0 }}>
              {mapUrls.map((url, idx) => (
                <div key={`map-${idx}-${url}`} style={{ border: '1px solid #e5e7eb', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0,0,0,0.08)', marginBottom: '1.5rem', background: '#fff', padding: '1rem' }}>
                  <iframe
                    src={url}
                    title={`Route ${idx + 1}`}
                    style={{ width: '100%', height: '600px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                    loading="lazy"
                  ></iframe>
                </div>
              ))}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              {legendHtmls && legendHtmls.map((legend, idx) => (
                <div key={`legend-${idx}`} style={{ background: '#f9fafb', borderRadius: '8px', padding: '1rem', marginBottom: '1rem', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
                  <div
                    style={{ fontSize: '0.95rem', color: '#374151', overflow: 'auto', maxHeight: '400px' }}
                    dangerouslySetInnerHTML={{ __html: legend }}
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
