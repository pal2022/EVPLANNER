import React from 'react';
import { NavLink } from 'react-router-dom';

export default function Menu() {
  return (
    <nav style={{ backgroundColor: 'lightblue', color: 'white', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', position: 'sticky', top: 0, zIndex: 50 }}>
      <div style={{ maxWidth: '80rem', margin: '0 auto', padding: '0.75rem 1rem', display: 'flex', justifyContent: 'flex-start', alignItems: 'center' }}>
        <div style={{ display: 'flex', fontSize: '1.5rem', gap: '2rem', alignItems: 'center' }}>
          <div style={{ fontWeight: 'bold', marginRight: '2rem' }}>
          ParetoRouteChoice
          </div>
          <NavLink
            to="/"
            style={({ isActive }) => ({
              textDecoration: isActive ? 'underline' : 'none',
              fontWeight: isActive ? '600' : 'normal',
              marginRight: '2rem'
            })}
          >
            Home
          </NavLink>
          <NavLink
            to="/map"
            style={({ isActive }) => ({
              textDecoration: isActive ? 'underline' : 'none',
              fontWeight: isActive ? '600' : 'normal',
              marginRight: '2rem'
            })}
          >
            Route
          </NavLink>
          <NavLink
            to="/contact"
            style={({ isActive }) => ({
              textDecoration: isActive ? 'underline' : 'none',
              fontWeight: isActive ? '600' : 'normal'
            })}
          >
            Contact Us
          </NavLink>
        </div>
      </div>
    </nav>
  );
}
