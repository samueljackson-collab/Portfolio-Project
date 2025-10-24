import { render, screen, waitFor } from "@testing-library/react";
import { rest } from "msw";
import { setupServer } from "msw/node";
import Profile from "../components/Profile";

const server = setupServer(
  rest.get("http://localhost:8000/users/me", (_req, res, ctx) => {
    return res(ctx.json({ name: "Alice", email: "alice@example.com" }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test("Profile displays user data after load", async () => {
  render(<Profile />);

  expect(screen.getByText(/Loading/)).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByText(/Welcome, Alice!/)).toBeInTheDocument();
  });

  expect(screen.getByText("alice@example.com")).toBeInTheDocument();
});
