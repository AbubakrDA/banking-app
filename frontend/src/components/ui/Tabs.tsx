import React, { createContext, useContext, useState, ReactNode } from 'react';

interface TabsContextType {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabsContext = createContext<TabsContextType>({
  activeTab: '',
  setActiveTab: () => {},
});

export interface TabsProps {
  defaultValue: string;
  children: ReactNode;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({ defaultValue, children, className = '' }) => {
  const [activeTab, setActiveTab] = useState<string>(defaultValue);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={`space-y-4 ${className}`}>{children}</div>
    </TabsContext.Provider>
  );
};

export const TabList: React.FC<{ children: ReactNode; className?: string }> = ({
  children,
  className = '',
}) => (
  <div className={`flex items-center space-x-1 border-b border-border-subtle ${className}`}>
    {children}
  </div>
);

export const TabTrigger: React.FC<{ value: string; children: ReactNode; className?: string }> = ({
  value,
  children,
  className = '',
}) => {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  const isActive = activeTab === value;

  return (
    <button
      type="button"
      onClick={() => setActiveTab(value)}
      className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition -mb-px ${
        isActive
          ? 'border-tealAccent text-tealAccent font-bold'
          : 'border-transparent text-navy-muted hover:text-navy hover:border-border-default'
      } ${className}`}
    >
      {children}
    </button>
  );
};

export const TabContent: React.FC<{ value: string; children: ReactNode; className?: string }> = ({
  value,
  children,
  className = '',
}) => {
  const { activeTab } = useContext(TabsContext);
  if (activeTab !== value) return null;

  return <div className={`pt-2 ${className}`}>{children}</div>;
};

export default Tabs;
