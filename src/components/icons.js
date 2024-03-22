'use client';

import React from 'react';
import '../styles/icons.css'; // Import your custom CSS file here

function IconArrowDown({ className, ...props }) {
  return (
    React.createElement("svg", Object.assign({
      xmlns: "http://www.w3.org/2000/svg",
      viewBox: "0 0 256 256",
      fill: "currentColor",
      className: "size-4 icon_arrow_down" // Apply your custom CSS classes directly here
    }, props), 
      React.createElement("path", { d: "m205.66 149.66-72 72a8 8 0 0 1-11.32 0l-72-72a8 8 0 0 1 11.32-11.32L120 196.69V40a8 8 0 0 1 16 0v156.69l58.34-58.35a8 8 0 0 1 11.32 11.32Z" })
    )
  );
}

function IconArrowElbow({ className, ...props }) {
    return (
      React.createElement("svg", Object.assign({
        xmlns: "http://www.w3.org/2000/svg",
        viewBox: "0 0 256 256",
        fill: "currentColor",
        className: "size-4 icon_arrow_elbow" // Apply your custom CSS classes directly here
      }, props), 
        React.createElement("path", { d: "M200 32v144a8 8 0 0 1-8 8H67.31l34.35 34.34a8 8 0 0 1-11.32 11.32l-48-48a8 8 0 0 1 0-11.32l48-48a8 8 0 0 1 11.32 11.32L67.31 168H184V32a8 8 0 0 1 16 0Z" })
      )
    );
}
  
export {
    IconArrowDown,
    IconArrowElbow
};
