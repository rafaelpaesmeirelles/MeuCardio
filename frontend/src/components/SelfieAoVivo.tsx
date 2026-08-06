import { useEffect, useRef, useState } from "react";

/** Captura de selfie PELA CÂMERA, ao vivo — pedido explícito do Rafael
 * (KYC, Trabalho 11/12): "implemente a Selfie ao vivo". De propósito NÃO
 * aceita upload de arquivo aqui — o objetivo é dificultar reenviar uma
 * foto qualquer no lugar da selfie do titular. Sem fallback de arquivo:
 * se a câmera não estiver disponível, o campo fica bloqueado com aviso
 * claro, em vez de abrir uma porta que anularia o propósito do campo. */
type Props = {
  arquivo: File | null;
  onCapturar: (arquivo: File) => void;
  onLimpar: () => void;
};

export default function SelfieAoVivo({ arquivo, onCapturar, onLimpar }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [ativa, setAtiva] = useState(false);
  const [erro, setErro] = useState("");
  const [preview, setPreview] = useState<string | null>(null);

  useEffect(() => {
    if (!arquivo) { setPreview(null); return; }
    const url = URL.createObjectURL(arquivo);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [arquivo]);

  function desligarCamera() {
    streamRef.current?.getTracks().forEach((faixa) => faixa.stop());
    streamRef.current = null;
    setAtiva(false);
  }

  useEffect(() => () => desligarCamera(), []);

  async function ligarCamera() {
    setErro("");
    if (!navigator.mediaDevices?.getUserMedia) {
      setErro("Este navegador não dá acesso à câmera. Tente pelo celular ou por outro navegador.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setAtiva(true);
    } catch {
      setErro("Não foi possível acessar a câmera — confira a permissão do navegador e tente de novo.");
    }
  }

  function capturar() {
    const video = videoRef.current;
    if (!video || !video.videoWidth) return;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => {
      if (!blob) return;
      onCapturar(new File([blob], `selfie-${Date.now()}.jpg`, { type: "image/jpeg" }));
      desligarCamera();
    }, "image/jpeg", 0.9);
  }

  function tirarNovamente() {
    onLimpar();
    ligarCamera();
  }

  return (
    <div style={{ marginTop: "0.8rem" }}>
      <label style={{ display: "block", marginBottom: "0.3rem" }}>Selfie ao vivo</label>
      <p className="eyebrow" style={{ margin: "0 0 0.5rem" }}>
        Tirada agora, pela câmera — não é possível enviar uma foto já existente aqui.
      </p>

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.84rem" }}>{erro}</p>}

      {preview ? (
        <div>
          <img src={preview} alt="Selfie capturada" style={{ width: "100%", maxWidth: 280, borderRadius: 8 }} />
          <div style={{ marginTop: "0.5rem" }}>
            <button type="button" className="botao botao--secundario" onClick={tirarNovamente}>
              Tirar novamente
            </button>
          </div>
        </div>
      ) : ativa ? (
        <div>
          {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
          <video ref={videoRef} autoPlay playsInline muted
                 style={{ width: "100%", maxWidth: 280, borderRadius: 8, background: "#000", transform: "scaleX(-1)" }} />
          <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem" }}>
            <button type="button" className="botao" onClick={capturar}>Capturar</button>
            <button type="button" className="botao botao--secundario" onClick={desligarCamera}>Cancelar</button>
          </div>
        </div>
      ) : (
        <button type="button" className="botao botao--secundario" onClick={ligarCamera}>
          Ligar câmera e tirar selfie
        </button>
      )}
    </div>
  );
}
