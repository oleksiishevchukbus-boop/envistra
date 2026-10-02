import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App'
import './index.css'

// A data router rather than <BrowserRouter>: `useBlocker`, which the unsaved-
// changes guard relies on, only works under one. The single catch-all route
// hands everything to App's own <Routes>, so the route table is unchanged.
const router = createBrowserRouter([{ path: '*', element: <App /> }])

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
