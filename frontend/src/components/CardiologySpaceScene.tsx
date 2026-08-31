export type CardiologySpaceSceneId =
  | "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao"
  | "descobrir" | "evidencias" | "aprender" | "ensinar" | "produzir";

function ClinicalInterior({ space }: { space: CardiologySpaceSceneId }) {
  if (space === "consultorio") return <g className="spaces-door__furniture">
    <path d="M72 103h86l12 12H59l13-12Zm-5 12v28m94-28v28M94 102V77h43v25M101 84h29M111 102V88" />
    <path d="M40 109h21v28H40zm5-1V96h20m-14 0v-9m-10 50h28M181 84h26v54h-26zM187 92h14m-14 10h14m-14 10h10" />
    <path d="M168 71c5-10 14-16 25-16m-17 28c-2-11 2-20 13-28m-14 28h24v5h-24Z" />
    <path className="spaces-door__lit" d="M49 54h35v27H49zm6 6h23v15H55m72-16h27m-27 8h20" />
    <circle cx="116" cy="94" r="3" />
  </g>;
  if (space === "hospital") return <g className="spaces-door__furniture">
    <path d="M49 111h97l18 13H37l12-13Zm0 13v17m107-17v17M64 110V93h61l19 18M66 100h28m43 5V79" />
    <path d="M176 74h30v68h-30zM182 83h18m-9-6v18M177 108h28M184 119h14" />
    <path d="M39 68h34v31H39zm6 6h22v18H45m11 7v12M36 111h41" />
    <path className="spaces-door__lit" d="M103 43v39m-18-26h36m-11-8v16m-14 0h28M48 82h8l4-7 7 14 5-7" />
    <path d="M154 56h14v29h-14m7-29v-8m-8 37h16" />
  </g>;
  if (space === "ensino") return <g className="spaces-door__furniture">
    <path d="M69 49h91v53H69zM77 57h75v37H77M114 102v13m-20 0h40" />
    <path className="spaces-door__lit" d="M87 68h22m-22 8h52m-52 8h39" />
    <path d="M37 126h43l6 12H30l7-12Zm8-21h27v21H45zm55 21h43l6 12H93l7-12Zm8-21h27v21h-27zm55 21h43l6 12h-56l7-12Zm8-21h27v21h-27z" />
    <path d="M52 116v-18m69 18V98m68 18V98" />
  </g>;
  if (space === "pesquisa") return <g className="spaces-door__furniture">
    <path d="M46 112h139l10 14H36l10-14Zm5 14v16m128-16v16" />
    <path d="M72 69h18v43H65l7-43Zm4 0v-10h10v10M70 91h22M112 78h24v34h-31l7-34Zm3 9h17" />
    <path d="M152 106V68m-12 0h31m-22-9c0-8 5-14 12-14s12 6 12 14v9h-24v-9ZM160 68l-9 20 19 12" />
    <path className="spaces-door__lit" d="M35 55h31v41H35zM41 63h19m-19 8h13m-13 8h17M102 54h25m-25 8h17" />
    <circle cx="161" cy="60" r="3" />
  </g>;
  if (space === "gestao") return <g className="spaces-door__furniture">
    <path d="M78 109h96l12 16H66l12-16Zm5 16v17m86-17v17M101 109V86h49v23" />
    <path d="M38 57h37v85H38zM46 126v-19h7v19m7 0V91h7v35" />
    <path d="M93 48h91v48H93zM102 87V72h9v15m10 0V61h9v26m10 0V74h9v13m10 0V65h9v22" />
    <path className="spaces-door__lit" d="M101 64c12-11 23-4 33-13 9-7 18-6 34-14M104 55h18m39 34h15" />
    <circle cx="168" cy="37" r="3" />
  </g>;
  return null;
}

function ScientificInterior({ space }: { space: CardiologySpaceSceneId }) {
  if (space === "descobrir") return <g className="spaces-door__furniture"><circle cx="106" cy="83" r="30"/><path d="m128 105 29 29M89 70c10-10 27-10 37 0M87 83h39M92 96c9 7 21 7 30 0"/><path d="M42 57h27v75H42zM48 67h15m-15 10h15m-15 10h11M175 53h27v79h-27zM181 64h15m-15 10h15m-15 10h11" className="spaces-door__lit"/></g>;
  if (space === "evidencias") return <g className="spaces-door__furniture"><path d="M45 52h56v80H45zM56 65h33M56 77h33M56 89h25M121 62h66v70h-66zM132 75h43m-43 12h43m-43 12h32"/><path d="m80 116 9 9 22-29M153 116l10-22 10 22m-15-8h11" className="spaces-door__lit"/></g>;
  if (space === "aprender") return <g className="spaces-door__furniture"><path d="m48 68 72-32 72 32-72 34Z"/><path d="M73 91v29c26 16 68 16 94 0V91M185 73v47"/><circle cx="185" cy="127" r="6" className="spaces-door__lit"/><path d="M64 140h112"/></g>;
  if (space === "ensinar") return <g className="spaces-door__furniture"><path d="M42 45h154v82H42zM53 57h132v57H53zM119 127v14m-35 0h70"/><path d="M69 99V82h15v17m14 0V68h15v31m14 0V75h15v24m14 0V61h15v38" className="spaces-door__lit"/></g>;
  return <g className="spaces-door__furniture"><path d="M50 48h86l27 27v66H50zM136 48v28h27M67 90h78M67 104h78M67 118h54"/><path d="m164 119 25-25 11 11-25 25-17 6Z" className="spaces-door__lit"/><path d="m172 98 11 11"/></g>;
}

export default function CardiologySpaceScene({ space }: { space: CardiologySpaceSceneId }) {
  const gradientId = `corvia-space-${space}`;
  const scientific = ["descobrir", "evidencias", "aprender", "ensinar", "produzir"].includes(space);
  return (
    <svg className="spaces-door__scene" data-space={space} viewBox="0 0 240 165" focusable="false" aria-hidden="true">
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="currentColor" stopOpacity=".15" />
          <stop offset="1" stopColor="currentColor" stopOpacity=".02" />
        </linearGradient>
      </defs>
      <path className="spaces-door__ambient" d="M18 156 42 24h156l24 132Z" fill={`url(#${gradientId})`} />
      <g className="spaces-door__architecture">
        <path d="M18 156 42 24h156l24 132M42 24l20 20h116l20-20M62 44v112m116-112v112M18 156h204" />
        <path d="M62 44 18 156m160-112 44 112M91 44l-12 112m70-112 12 112M27 132h186" opacity=".52" />
        <path d="M82 18h76M92 26h56M102 34h36" className="spaces-door__ceiling spaces-door__lit" />
        <path d="M28 144h184M38 121h164M48 98h144M58 76h124" opacity=".24" />
        <path d="M80 156 94 44m66 112-14-112M119 156V44" opacity=".2" />
      </g>
      {scientific ? <ScientificInterior space={space} /> : <ClinicalInterior space={space} />}
      <g className="spaces-door__depth-points">
        <circle cx="62" cy="44" r="1.7" /><circle cx="178" cy="44" r="1.7" />
        <circle cx="18" cy="156" r="1.7" /><circle cx="222" cy="156" r="1.7" />
      </g>
    </svg>
  );
}
