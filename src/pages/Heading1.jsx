import React, { useState } from 'react';

export default function Heading1() {
  const [isTableExpanded, setIsTableExpanded] = useState(false);

  return (
    <>
      <section className="max-w-4xl mx-auto text-center py-16 px-6">
        <h1 className="text-4xl md:text-5xl font-bold text-blue-700 mb-4">
          Your Route, Your Rules
        </h1>
        <p className="text-gray-600 text-lg md:text-xl">
          Plan your electric vehicle routes with optimized battery usage, charging stops, and real map visualizations.
        </p>
      </section>

      {/*Key Features Section*/}
      <section className="bg-white py-12">
        <div className="max-w-6xl mx-auto px-6">
          <h4 className="text-2xl md:text-3xl font-semibold text-center mb-12 text-gray-900">
            Smart EV Route Planning for British Columbia
          </h4>
          <div className="grid grid-cols-3 gap-8 text-center">
            <div className="flex flex-col items-center p-6 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 hover:shadow-xl hover:scale-105 hover:bg-gradient-to-br hover:from-blue-100 hover:to-indigo-100 transition-all duration-300 ease-in-out cursor-pointer group">
              <div className="text-5xl mb-4 text-blue-600 group-hover:text-blue-700 group-hover:scale-110 transition-all duration-300">🔋</div>
              <h5 className="text-lg font-semibold text-gray-900 group-hover:text-blue-800 transition-colors duration-300">Battery-Aware Routing</h5>
              <p className="text-sm text-gray-600 mt-2 group-hover:text-gray-700 transition-colors duration-300">Plan routes with real-time battery consumption <br/> tracking and charging station proximity.</p>
            </div>
            <div className="flex flex-col items-center p-6 rounded-xl bg-gradient-to-br from-green-50 to-emerald-50 hover:shadow-xl hover:scale-105 hover:bg-gradient-to-br hover:from-green-100 hover:to-emerald-100 transition-all duration-300 ease-in-out cursor-pointer group">
              <div className="text-5xl mb-4 text-green-600 group-hover:text-green-700 group-hover:scale-110 transition-all duration-300">⚡</div>
              <h5 className="text-lg font-semibold text-gray-900 group-hover:text-green-800 transition-colors duration-300">Multi-Route Optimization</h5>
              <p className="text-sm text-gray-600 mt-2 group-hover:text-gray-700 transition-colors duration-300">Get multiple route options balancing travel time and safety <br/>with charging station access.</p>
            </div>
            <div className="flex flex-col items-center p-6 rounded-xl bg-gradient-to-br from-purple-50 to-violet-50 hover:shadow-xl hover:scale-105 hover:bg-gradient-to-br hover:from-purple-100 hover:to-violet-100 transition-all duration-300 ease-in-out cursor-pointer group">
              <div className="text-5xl mb-4 text-purple-600 group-hover:text-purple-700 group-hover:scale-110 transition-all duration-300">🗺️</div>
              <h5 className="text-lg font-semibold text-gray-900 group-hover:text-purple-800 transition-colors duration-300">Interactive Maps</h5>
              <p className="text-sm text-gray-600 mt-2 group-hover:text-gray-700 transition-colors duration-300">Visualize routes with detailed maps showing <br/> charging stations and critical battery points.</p>
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
            <h2 className="flex-1 text-base font-semibold text-gray-800 text-center">How to Use EV Route Planner</h2>
            <span className="text-gray-500 text-2xl transition-transform duration-200">
              {isTableExpanded ? '−' : '+'}
            </span>
          </button>
          
          {/* Collapsible Content */}
          {isTableExpanded && (
            <div className="transition-all duration-300 ease-in-out overflow-hidden max-h-screen opacity-100">
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
          )}
        </div>
      </section>

    </>
  );
}
