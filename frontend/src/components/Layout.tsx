import { Outlet, Navigate } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function Layout() {
  const token = localStorage.getItem('token')
  if (!token) return <Navigate to="/login" />

  return (
    <div style={{ display: 'flex' }}>
      <Sidebar />
      <main style={{ marginLeft: 260, flex: 1, padding: 24, minHeight: '100vh' }}>
        <Outlet />
      </main>
    </div>
  )
}
