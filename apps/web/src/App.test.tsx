import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "./App";

describe("App", () => {
  it("renders the OpenVend dashboard shell", () => {
    render(<App />);

    expect(screen.getByText("OpenVend")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByText("Phase 0 service map")).toBeInTheDocument();
  });
});
