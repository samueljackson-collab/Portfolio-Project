import { render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import Home from "./Home";

vi.mock("../lib/api", () => ({
  fetchHealth: vi.fn().mockResolvedValue({ status: "ok" }),
}));

describe("Home", () => {
  it("renders health status", async () => {
    render(<Home />);
    expect(screen.getByText(/Checking/)).toBeInTheDocument();

    await waitFor(() => expect(screen.getByText(/API is healthy/)).toBeInTheDocument());
  });
});
