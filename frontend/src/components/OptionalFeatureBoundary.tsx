import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = { children: ReactNode; nome: string };
type State = { falhou: boolean };

/** Impede que um aprimoramento opcional derrube o acesso ao sistema. */
export default class OptionalFeatureBoundary extends Component<Props, State> {
  state: State = { falhou: false };

  static getDerivedStateFromError(): State {
    return { falhou: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(`Recurso opcional indisponível: ${this.props.nome}`, error.name, info.componentStack);
  }

  render() {
    return this.state.falhou ? null : this.props.children;
  }
}
