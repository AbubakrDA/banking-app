import React, { useState, useEffect, ReactNode } from 'react';
import { RouterContext, useRouter } from './hooks';

interface RouterProps {
  children: ReactNode;
  initialPath?: string;
}

export const Router: React.FC<RouterProps> = ({ children, initialPath }) => {
  const [path, setPath] = useState<string>(() => {
    if (initialPath) return initialPath;
    if (typeof window !== 'undefined' && window.location) {
      return window.location.pathname || '/';
    }
    return '/';
  });

  useEffect(() => {
    const handlePopState = () => {
      setPath(window.location.pathname || '/');
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (to: string) => {
    if (typeof window !== 'undefined' && window.history) {
      window.history.pushState({}, '', to);
    }
    setPath(to);
  };

  return (
    <RouterContext.Provider value={{ path, navigate }}>
      {children}
    </RouterContext.Provider>
  );
};

interface LinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  to: string;
  children: ReactNode;
  className?: string;
}

export const Link: React.FC<LinkProps> = ({ to, children, className, onClick, ...rest }) => {
  const { navigate } = useRouter();

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (onClick) onClick(e);
    if (!e.defaultPrevented && e.button === 0 && !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey) {
      e.preventDefault();
      navigate(to);
    }
  };

  return (
    <a href={to} onClick={handleClick} className={className} {...rest}>
      {children}
    </a>
  );
};

interface NavLinkProps extends Omit<LinkProps, 'className'> {
  className?: string | ((props: { isActive: boolean }) => string);
}

export const NavLink: React.FC<NavLinkProps> = ({ to, children, className, ...rest }) => {
  const { path } = useRouter();
  const isActive = path === to || (to !== '/' && path.startsWith(to));

  const resolvedClassName = typeof className === 'function' ? className({ isActive }) : className;

  return (
    <Link to={to} className={resolvedClassName} {...rest}>
      {children}
    </Link>
  );
};

interface RouteProps {
  path: string;
  element: ReactNode;
}

export const Route: React.FC<RouteProps> = ({ element }) => {
  return <>{element}</>;
};

interface RoutesProps {
  children: ReactNode;
}

export const Routes: React.FC<RoutesProps> = ({ children }) => {
  const { path } = useRouter();
  let defaultMatch: ReactNode = null;
  let matchedElement: ReactNode = null;

  React.Children.forEach(children, (child) => {
    if (!React.isValidElement<RouteProps>(child)) return;
    const routePath = child.props.path;
    if (routePath === '*') {
      defaultMatch = child.props.element;
    } else if (routePath === path) {
      matchedElement = child.props.element;
    }
  });

  return <>{matchedElement || defaultMatch || null}</>;
};
