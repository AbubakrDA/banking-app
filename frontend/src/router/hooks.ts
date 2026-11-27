import { createContext, useContext } from 'react';

export interface RouterContextType {
  path: string;
  navigate: (to: string) => void;
}

export const RouterContext = createContext<RouterContextType>({
  path: '/',
  navigate: () => {},
});

export const useRouter = () => useContext(RouterContext);

export const useLocation = () => {
  const { path } = useRouter();
  return { pathname: path };
};

export const useNavigate = () => {
  const { navigate } = useRouter();
  return navigate;
};
