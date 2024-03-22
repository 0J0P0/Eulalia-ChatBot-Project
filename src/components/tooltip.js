"use client";

import React from "react";
import * as TooltipPrimitive from "@radix-ui/react-tooltip";

import "../styles/tooltip.css";
// import { cn } from "../utils/utils.js";

const TooltipProvider = TooltipPrimitive.Provider;
const Tooltip = TooltipPrimitive.Root;
const TooltipTrigger = TooltipPrimitive.Trigger;

const TooltipContent = React.forwardRef(
  (
    { className, sideOffset = 4, ...props },
    ref
  ) => (
    <TooltipPrimitive.Content
      ref={ref}
      sideOffset={sideOffset}
      className='tooltip_content'
      {...props}
    />
  )
);
TooltipContent.displayName = TooltipPrimitive.Content.displayName;

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider };
