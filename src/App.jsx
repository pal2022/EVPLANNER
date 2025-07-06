import React from "react";
import { Routes, Route } from "react-router-dom";
import Menu from "./components/Menu";
import Heading1 from "./pages/Heading1";
import Map from "./pages/Map";
import ContactUs from "./pages/ContactUs";

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Menu />

      <main className="flex-grow px-4 py-8">
        <Routes>
          <Route path="/" element={<Heading1 />} />
          <Route path="/map" element={<Map />} />
          <Route path="/contact" element={<ContactUs />} />
        </Routes>
      </main>

      <footer className="text-center py-6 text-gray-500 text-sm border-t">
        &copy; {new Date().getFullYear()} EV Planner. All rights reserved.
      </footer>
    </div>
  );
}

export default App;
