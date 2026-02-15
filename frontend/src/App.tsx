import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import JobsPage from './pages/Jobs';
import ProfilePage from './pages/Profile';
import ScrapePage from './pages/Scrape';
import ChatPage from './pages/Chat';
import CompanySearchPage from './pages/CompanySearchPage';
import EmailsPage from './pages/EmailsPage';
import SettingsPage from './pages/Settings';

import { WebSocketProvider } from './context/WebSocketProvider';

function App() {
  return (
    <Router>
      <WebSocketProvider>
        <Routes>
          <Route path="/" element={<Layout><Dashboard /></Layout>} />
          <Route path="/jobs" element={<Layout><JobsPage /></Layout>} />
          <Route path="/search" element={<Layout><CompanySearchPage /></Layout>} />
          <Route path="/profile" element={<Layout><ProfilePage /></Layout>} />
          <Route path="/scrape" element={<Layout><ScrapePage /></Layout>} />
          <Route path="/chat" element={<Layout><ChatPage /></Layout>} />
          <Route path="/emails" element={<Layout><EmailsPage /></Layout>} />
          <Route path="/documents" element={<Layout><div className="p-4">Document Manager (Coming Soon)</div></Layout>} />
          <Route path="/settings" element={<Layout><SettingsPage /></Layout>} />
        </Routes>
      </WebSocketProvider>
    </Router>
  );
}

export default App;
