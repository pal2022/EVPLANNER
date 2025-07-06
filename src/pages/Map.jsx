import React from 'react';
import Form from '../components/Form';

export default function Map() {
  return (
    <section className="max-w-4xl mx-auto px-4 py-10">
      <h2 className="text-3xl font-semibold text-center text-blue-700 mb-8">
        Plan Your EV Route
      </h2>
      <Form />
    </section>
  );
}
