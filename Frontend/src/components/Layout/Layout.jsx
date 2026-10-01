import React, { useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Navbar from '../Navbar/Navbar';
import Footer from '../Footer/Footer';

export function Layout() {
  const { pathname } = useLocation();

  // Automatically scroll to top on route navigation
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return (
    <div className="app-root">
      <Navbar />
      <main className="page-wrapper">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

export default Layout;
