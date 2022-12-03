import { Route, Routes, BrowserRouter } from "react-router-dom";

import Layout from './pages/Layout.jsx';
import NotFound from './pages/NotFound.jsx';
import HikesBrowser from './pages/HikesBrowser.jsx';
import TestPage from './pages/TestPage.jsx';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HikesBrowser />} />
          <Route path="test" element={<TestPage />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

// vim: set sw=2 ts=2 expandtab:
