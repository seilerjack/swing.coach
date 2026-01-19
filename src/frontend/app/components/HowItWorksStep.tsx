
import { LucideIcon } from "lucide-react";

type Props = {
  step: number;
  icon: LucideIcon;
  title: string;
  description: string;
};

export default function HowItWorksStep({
  step,
  icon: Icon,
  title,
  description,
}: Props) {
  return (
    <div className="flex flex-col items-center text-center max-w-xs">
      {/* Icon Circle */}
      <div className="relative mb-6">
        <div className="w-16 h-16 rounded-full bg-black flex items-center justify-center">
          <Icon className="w-7 h-7 text-white" />
        </div>

        {/* Step Number */}
        <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-white border border-black flex items-center justify-center text-xs font-semibold">
          {step}
        </div>
      </div>

      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}
