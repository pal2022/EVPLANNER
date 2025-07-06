import React, { useState } from 'react';

export default function Heading1() {
  const [isTableExpanded, setIsTableExpanded] = useState(false);

  return (
    <>
      <section className="max-w-4xl mx-auto text-center py-16 px-6">
        <h1 className="text-4xl md:text-5xl font-bold text-blue-700 mb-4">
          Welcome to EV Route Planner
        </h1>
        <p className="text-gray-600 text-lg md:text-xl">
          Plan your electric vehicle routes with optimized battery usage, charging stops, and real map visualizations.
        </p>
      </section>

      {/*Key Features Section*/}
      <section className="bg-white py-12">
        <div className="max-w-6xl mx-auto px-6">
          <h4 className="text-2xl md:text-3xl font-semibold text-center mb-12 text-gray-900">
            Customize routes for your needs.
          </h4>
          <div className="grid grid-cols-3 gap-8 text-center">
            <div className="flex flex-col items-center">
              <div className="text-5xl mb-4 text-blue-600">📍</div>
              <h5 className="text-lg font-semibold text-gray-900">Multi-City</h5>
              <p className="text-sm text-gray-600 mt-2">Plan trips across cities and regions with ease.</p>
            </div>
            <div className="flex flex-col items-center">
              <div className="text-5xl mb-4 text-blue-600">🚗</div>
              <h5 className="text-lg font-semibold text-gray-900">Flexible Modes</h5>
              <p className="text-sm text-gray-600 mt-2">Switch between safety, speed, and scenic routes.</p>
            </div>
            <div className="flex flex-col items-center">
              <div className="text-5xl mb-4 text-blue-600">📆</div>
              <h5 className="text-lg font-semibold text-gray-900">Anytime Year-round</h5>
              <p className="text-sm text-gray-600 mt-2">Route planning that works in all seasons.</p>
            </div>
          </div>
        </div>
      </section>



      {/* Collapsible Table Section */}
      <section className="max-w-6xl mx-auto py-8 px-6">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Dropdown Header */}
          <button
            onClick={() => setIsTableExpanded(!isTableExpanded)}
            className="w-full px-6 py-4 text-left bg-gray-50 hover:bg-gray-100 transition-colors duration-200 flex justify-between items-center"
          >
            <h2 className="text-xl font-semibold text-gray-800">How to Use EV Route Planner</h2>
            <span className="text-gray-500 text-2xl transition-transform duration-200">
              {isTableExpanded ? '−' : '+'}
            </span>
          </button>
          
          {/* Collapsible Content */}
          <div className={`transition-all duration-300 ease-in-out overflow-hidden ${
            isTableExpanded ? 'max-h-screen opacity-100' : 'max-h-0 opacity-0'
          }`}>
            <table className="w-full">
              <tbody>
                <tr className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="bg-gray-100 rounded-lg p-4 text-center">
                      <img 
                        src="/src/images/image1.png" 
                        alt="Route input form" 
                        className="w-1/3 h-auto object-cover rounded-lg mx-auto"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'block';
                        }}
                      />
                      <div className="text-gray-500 text-sm mt-2" style={{display: 'none'}}>
                        📷 Image: Route input form will go here
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="bg-gray-100 rounded-lg p-4 text-center">
                      <img 
                        src="/src/assets/map-screenshot.png" 
                        alt="Map with multiple routes" 
                        className="w-1/3 h-auto object-cover rounded-lg mx-auto"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'block';
                        }}
                      />
                      <div className="text-gray-500 text-sm mt-2" style={{display: 'none'}}>
                        📷 Image: Map with multiple routes will go here
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="bg-gray-100 rounded-lg p-4 text-center">
                      <img 
                        src="/src/assets/legend-screenshot.png" 
                        alt="Route legend and details" 
                        className="w-1/3 h-auto object-cover rounded-lg mx-auto"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'block';
                        }}
                      />
                      <div className="text-gray-500 text-sm mt-2" style={{display: 'none'}}>
                        📷 Image: Route legend and details will go here
                      </div>
                    </div>
                  </td>
                </tr>
                <tr className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <h3 className="text-lg font-semibold mb-2">Step 1: Enter Your Details</h3>
                    <ul className="text-gray-600 space-y-1 text-left text-sm">
                      <li>Choose your starting location and destination</li>
                      <li>Select your EV model for accurate energy consumption</li>
                      <li>Currently supports BC regions (Southwestern & Northeastern)</li>
                    </ul>
                  </td>
                  <td className="px-6 py-4">
                    <h3 className="text-lg font-semibold mb-2">Step 2: Get Optimal Routes</h3>
                    <ul className="text-gray-600 space-y-1 text-left text-sm">
                      <li>Multiple route options with different trade-offs</li>
                      <li>Balance between travel time and charging station proximity</li>
                      <li>Automatic charging stop recommendations</li>
                    </ul>
                  </td>
                  <td className="px-6 py-4">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">Step 3: Understand Your Results</h3>
                    <ul className="text-gray-600 space-y-1 text-left text-sm">
                      <li>Color-coded routes on the map</li>
                      <li>Detailed legend with travel time and safety metrics</li>
                      <li>Battery level predictions and charging time estimates</li>
                    </ul>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

    </>
  );
}
