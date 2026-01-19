
import { ReactElement } from "react";

type FeatureCardProps = {
  icon: ReactElement;
  title: string;
  description: string;
};

export default function FeatureCard({
  icon,
  title,
  description,
}: FeatureCardProps) {
  return (
    <div className="
      rounded-xl border bg-white p-6 shadow-sm
      transition-all duration-200
      hover:scale-105 active:scale-95
      ">
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
        {icon}
      </div>
      <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}
