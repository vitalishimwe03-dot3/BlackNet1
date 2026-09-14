import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { formatBytes, formatStorage, timeAgo } from "../utils/format";
import { StatusDot } from "../components/StatusDot";
import { Avatar } from "../components/Avatar";

describe("format utils", () => {
  it("formats bytes correctly", () => {
    expect(formatBytes(0)).toBe("0 B");
    expect(formatBytes(1024)).toBe("1.00 KB");
    expect(formatBytes(5 * 1024 ** 3)).toBe("5.00 GB");
  });

  it("formats storage totals", () => {
    expect(formatStorage(5 * 1024 ** 3)).toBe("5.00 GB");
  });

  it("formats relative time", () => {
    expect(timeAgo(new Date().toISOString())).toBe("JUST NOW");
  });
});

describe("status indicator", () => {
  it("shows online state", () => {
    render(<StatusDot online />);
    expect(screen.getByLabelText("online")).toBeInTheDocument();
  });

  it("shows offline state", () => {
    render(<StatusDot online={false} />);
    expect(screen.getByLabelText("offline")).toBeInTheDocument();
  });
});

describe("avatar", () => {
  it("renders initials fallback", () => {
    render(<Avatar username="vector" />);
    expect(screen.getByText("VE")).toBeInTheDocument();
  });
});