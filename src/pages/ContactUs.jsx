import React from 'react';

export default function ContactUs() {
  return (
    <section className="max-w-3xl mx-auto text-center py-16 px-6">
      <h1 className="text-3xl md:text-4xl font-bold text-blue-700 mb-4">
        Contact Us
      </h1>
      <p className="text-gray-600 text-lg">
        We'd love to hear from you! Reach out for support, feedback, or collaboration.
      </p>
      <div className="mt-6 space-y-3 text-gray-700 text-base">
        <div className="space-y-2">
          <p>
            <strong>Palkan Motwani</strong> •{" "}
            <a href="mailto:palkan142000@gmail.com" className="text-blue-500 underline">
              palkan142000@gmail.com
            </a>{" "}
            •{" "}
            <a href="https://linkedin.com/in/palkan-motwani" target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">
              LinkedIn
            </a>
          </p>
          <p>
            <strong>Zi Hao Li</strong> •{" "}
            <a href="mailto:zihaoli17@yahoo.ca" className="text-blue-500 underline">
              zihaoli17@yahoo.ca
            </a>{" "}
            •{" "}
            <a href="https://www.linkedin.com/in/zi-hao-li-1b2932225/" target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">
              LinkedIn
            </a>
          </p>
          <p>
            <strong>Mario Nascimento</strong> •{" "}
            <a href="mailto:m.nascimento@northeastern.edu" className="text-blue-500 underline">
              m.nascimento@northeastern.edu
            </a>
            •{" "}
            <a href="" target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">
              LinkedIn
            </a>
          </p>
        </div>
        
        <div className="mt-6">
          <p className="text-lg">
            🐙 <strong>GitHub:</strong>{" "}
            <a href="https://github.com/pal2022/EVPLANNER" target="_blank" rel="noopener noreferrer" className="text-blue-500 underline font-semibold">
              github.com/evplanner
            </a>
          </p>
        </div>
        
        <p>📍 Location: Vancouver, BC</p>
      </div>
    </section>
  );
}
