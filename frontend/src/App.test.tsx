import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

describe('BankingAIPlatform AppShell, Navigation & Module Views Verification (Task 1.4 & 1.5)', () => {
  it('renders the BankingAIPlatform brand header and tenant context badge', () => {
    render(<App />);
    expect(screen.getByText('BankingAIPlatform')).toBeInTheDocument();
    expect(screen.getByText('Acme Global Ltd')).toBeInTheDocument();
    expect(screen.getByText('Alex Chen')).toBeInTheDocument();
  });

  it('renders all 9 approved module navigation links in the sidebar', () => {
    render(<App />);
    expect(screen.getByRole('link', { name: /Admin Intelligence/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /AI Chat Agent/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Knowledge Base/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Business Data Hub/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Customer Management/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Complaints & Tickets/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Integrations & Tools/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Cloud & Infrastructure/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Enterprise Administration/i })).toBeInTheDocument();
  });

  it('toggles sidebar collapse state when clicking the chevron toggle', () => {
    render(<App />);
    const collapseButton = screen.getByRole('button', { name: /Collapse Sidebar/i });
    expect(collapseButton).toBeInTheDocument();

    // Click collapse
    fireEvent.click(collapseButton);
    expect(screen.getByRole('button', { name: /Expand Sidebar/i })).toBeInTheDocument();

    // Click expand
    const expandButton = screen.getByRole('button', { name: /Expand Sidebar/i });
    fireEvent.click(expandButton);
    expect(screen.getByRole('button', { name: /Collapse Sidebar/i })).toBeInTheDocument();
  });

  it('navigates to AI Chat Agent and renders the 3-column workspace', () => {
    render(<App />);
    const chatLink = screen.getByRole('link', { name: /AI Chat Agent/i });
    fireEvent.click(chatLink);

    expect(screen.getByRole('heading', { name: /AI Customer Support Chat Workspace/i, level: 1 })).toBeInTheDocument();
    expect(screen.getAllByText(/Sarah Jenkins/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Customer Context & Memory/i)).toBeInTheDocument();
    expect(screen.getByText(/Grounded in Business Hub/i)).toBeInTheDocument();
  });

  it('navigates to Business Data Hub and allows toggling business model configuration', () => {
    render(<App />);
    const dataHubLink = screen.getByRole('link', { name: /Business Data Hub/i });
    fireEvent.click(dataHubLink);

    expect(screen.getByRole('heading', { name: /Business Data Hub/i, level: 1 })).toBeInTheDocument();
    expect(screen.getByText(/Organization Business Model Configuration/i)).toBeInTheDocument();

    // Toggle business mode to "Products Only"
    const productsCard = screen.getByText('Products Only');
    fireEvent.click(productsCard);
    expect(screen.getByText(/SKUs, catalog, stock quantities/i)).toBeInTheDocument();
  });

  it('navigates to Knowledge Base and displays collections and pgvector status', () => {
    render(<App />);
    const kbLink = screen.getByRole('link', { name: /Knowledge Base/i });
    fireEvent.click(kbLink);

    expect(screen.getByRole('heading', { name: /Knowledge Base & RAG Index/i, level: 1 })).toBeInTheDocument();
    expect(screen.getAllByText(/Indexed \(pgvector\)/i).length).toBeGreaterThan(0);
  });

  it('navigates to Integrations & Tools and displays Tool Gateway risk tiers', () => {
    render(<App />);
    const toolsLink = screen.getByRole('link', { name: /Integrations & Tools/i });
    fireEvent.click(toolsLink);

    expect(screen.getByRole('heading', { name: /Tool Gateway & Integrations Registry/i, level: 1 })).toBeInTheDocument();
    expect(screen.getByText(/LOW Risk Tools/i)).toBeInTheDocument();
    expect(screen.getByText(/HIGH Risk Tools/i)).toBeInTheDocument();
  });

  it('navigates to Enterprise Admin and verifies branding inputs', () => {
    render(<App />);
    const adminLink = screen.getByRole('link', { name: /Enterprise Administration/i });
    fireEvent.click(adminLink);

    expect(screen.getByRole('heading', { name: /Enterprise Administration/i, level: 1 })).toBeInTheDocument();
    expect(screen.getByLabelText(/Company \/ Organization Name/i)).toHaveValue('Acme Global Ltd');
  });
});
