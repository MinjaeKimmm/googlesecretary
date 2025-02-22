'use client';

import { useEffect, useState, useContext } from "react";
import { ViewerContext } from "../../features/vrmViewer/viewerContext";

interface VrmViewerProps {
  selectedCharacter: string; // ✅ 캐릭터 선택 prop 추가
}

export default function VrmViewer({ selectedCharacter }: VrmViewerProps) {
  const { viewer } = useContext(ViewerContext);
  const [currentCharacter, setCurrentCharacter] = useState("");

  // ✅ 캐릭터 URL 매핑
  const modelUrls: Record<string, string> = {
    Bunny: "/models/bunny.vrm",
    Shortcut: "/models/shortcut.vrm",
    Wolf: "/models/wolf.vrm",
    Teenager: "/models/teenager.vrm",
    Tuxedo: "/models/tuxido.vrm",
    Yukata: "/models/yukata.vrm",
  };

  useEffect(() => {
    if (viewer && selectedCharacter !== currentCharacter) {
      console.log(`🔄 캐릭터 변경: ${selectedCharacter}`);
      setCurrentCharacter(selectedCharacter);
      viewer.loadVrm(modelUrls[selectedCharacter] || "/models/dummy.vrm");
    }
  }, [selectedCharacter, viewer]);

  return (
    <div className="h-full w-ull z-10">
      <canvas className="h-full w-full"></canvas>
    </div>
  );
}
