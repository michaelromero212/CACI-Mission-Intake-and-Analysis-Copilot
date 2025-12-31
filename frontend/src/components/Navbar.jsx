import { NavLink } from 'react-router-dom';

/**
 * Main navigation component with CACI branding.
 * Includes classification banner for government environment.
 */
export default function Navbar() {
    return (
        <>
            {/* Classification Banner - Standard in government systems */}
            <div className="classification-banner">
                UNCLASSIFIED // FOR DEMONSTRATION PURPOSES ONLY
            </div>

            <nav className="navbar">
                <NavLink to="/" className="navbar-brand">
                    <div className="logo-icon">🛡️</div>
                    <span>CACI Mission Copilot</span>
                </NavLink>

                <div className="navbar-nav">
                    <NavLink
                        to="/"
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                        title="Keyboard: N"
                    >
                        Mission Intake
                        <span style={{
                            marginLeft: '0.375rem',
                            fontSize: '0.625rem',
                            opacity: 0.5,
                            fontFamily: 'var(--font-mono)'
                        }}>(N)</span>
                    </NavLink>
                    <NavLink
                        to="/history"
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                        title="Keyboard: H"
                    >
                        Mission Registry
                        <span style={{
                            marginLeft: '0.375rem',
                            fontSize: '0.625rem',
                            opacity: 0.5,
                            fontFamily: 'var(--font-mono)'
                        }}>(H)</span>
                    </NavLink>
                </div>
            </nav>
        </>
    );
}
