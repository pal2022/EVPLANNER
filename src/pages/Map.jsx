import React, { useState } from 'react';
import Form from '../components/Form';
import MapSelector from '../components/MapSelector';

export default function Map() {
  const [start, setStart] = useState('');
  const [destination, setDestination] = useState('');

  return (
    <section className="max-w-7xl mx-auto px-4 py-10">
      <h2 className="text-3xl font-semibold text-center text-blue-700 mb-8">
        Plan Your EV Route
      </h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="w-full">
          <Form
            start={start}
            destination={destination}
            onStartChange={setStart}
            onDestinationChange={setDestination}
          />
        </div>
        <div className="w-full">
          <MapSelector
            start={start}
            destination={destination}
            onStartChange={setStart}
            onDestinationChange={setDestination}
          />
        </div>
      </div>
    </section>
  );
}
