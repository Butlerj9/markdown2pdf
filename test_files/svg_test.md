# SVG Embedding Test

This document tests SVG embedding.

## Inline SVG

<svg width="100" height="100">
  <circle cx="50" cy="50" r="40" stroke="black" stroke-width="2" fill="red" />
</svg>

## Complex SVG

<svg width="200" height="200" viewBox="0 0 200 200">
  <rect x="10" y="10" width="180" height="180" fill="#f0f0f0" stroke="black" stroke-width="2" />
  <circle cx="100" cy="100" r="80" fill="#d0d0ff" stroke="blue" stroke-width="2" />
  <polygon points="100,30 150,150 50,150" fill="#ffe0e0" stroke="red" stroke-width="2" />
  <text x="100" y="100" text-anchor="middle" font-family="Arial" font-size="16">SVG Test</text>
</svg>

## SVG with Animation

<svg width="200" height="100">
  <rect width="200" height="100" fill="#f0f0f0" />
  <circle cx="50" cy="50" r="40" stroke="black" stroke-width="2" fill="yellow">
    <animate attributeName="r" values="40;20;40" dur="2s" repeatCount="indefinite" />
  </circle>
  <circle cx="150" cy="50" r="20" stroke="black" stroke-width="2" fill="blue">
    <animate attributeName="r" values="20;40;20" dur="2s" repeatCount="indefinite" />
  </circle>
</svg>
