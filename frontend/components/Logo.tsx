import Image from "next/image";

interface LogoProps {
  variant?: "full" | "icon";
  className?: string;
  height?: number;
  width?: number;
}

export function Logo({
  variant = "full",
  className = "",
  height,
  width,
}: LogoProps) {
  const logoSrc = variant === "full" ? "/logo.svg" : "/icon.svg";

  // Dimensiones por defecto basadas en el variant
  const defaultHeight = variant === "full" ? 40 : 32;
  const defaultWidth = variant === "full" ? 180 : 60;

  return (
    <Image
      src={logoSrc}
      alt="SYNCAR Logo"
      height={height || defaultHeight}
      width={width || defaultWidth}
      className={className}
      priority
    />
  );
}
