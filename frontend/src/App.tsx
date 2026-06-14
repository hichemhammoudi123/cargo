import { Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from './layouts/DashboardLayout'
import AuthGuard from './components/AuthGuard'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Rates from './pages/Rates'
import Shipments from './pages/Shipments'
import ShipmentDetail from './pages/ShipmentDetail'
import Tracking from './pages/Tracking'
import Carriers from './pages/Carriers'
import CarrierDetail from './pages/CarrierDetail'
import Pickups from './pages/Pickups'
import WebhookLogs from './pages/WebhookLogs'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<AuthGuard><DashboardLayout /></AuthGuard>}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/rates" element={<Rates />} />
        <Route path="/shipments" element={<Shipments />} />
        <Route path="/shipments/:id" element={<ShipmentDetail />} />
        <Route path="/tracking/:id" element={<Tracking />} />
        <Route path="/carriers" element={<Carriers />} />
        <Route path="/carriers/:code" element={<CarrierDetail />} />
        <Route path="/pickups" element={<Pickups />} />
        <Route path="/webhooks" element={<WebhookLogs />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
