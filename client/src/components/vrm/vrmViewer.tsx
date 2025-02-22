import { useContext, useCallback, useEffect } from "react";
import { ViewerContext } from "../../features/vrmViewer/viewerContext";

interface VrmViewerProps {
  selectedCharacter: string;
}

export default function VrmViewer({selectedCharacter}: VrmViewerProps) {
  const { viewer } = useContext(ViewerContext);

  const modelUrls: Record<string, string> = {
    Bunny: "/models/bunny.vrm",
    Shortcut: "/models/shortcut.vrm",
    Wolf: "/models/wolf.vrm",
    Teenager: "/models/teenager.vrm",
    Tuxido: "/models/tuxido.vrm",
    Yukata: "/models/yukata.vrm",
  };

  useEffect(() => {
    if (viewer && selectedCharacter) {
      console.log(`🔄 모델 변경: ${selectedCharacter}`);
      const modelUrl = modelUrls[selectedCharacter] || "/models/dummy.vrm";
      viewer.loadVrm(modelUrl);
    }
  }, [selectedCharacter, viewer]);

  const canvasRef = useCallback(
    (canvas: HTMLCanvasElement) => {
      if (canvas) {
        viewer.setup(canvas);
  
        // ✅ modelUrls에서 현재 선택된 캐릭터에 해당하는 URL을 가져오기
        const modelUrl = modelUrls[selectedCharacter] || "/models/dummy.vrm";
        console.log(`🔄 VRM 로드: ${modelUrl}`);
  
        viewer.loadVrm(modelUrl);
  
        // Drag and DropでVRMを差し替え
        canvas.addEventListener("dragover", function (event) {
          event.preventDefault();
        });
  
        canvas.addEventListener("drop", function (event) {
          event.preventDefault();
  
          const files = event.dataTransfer?.files;
          if (!files) {
            return;
          }
  
          const file = files[0];
          if (!file) {
            return;
          }
  
          const file_type = file.name.split(".").pop();
          if (file_type === "vrm") {
            const blob = new Blob([file], { type: "application/octet-stream" });
            const url = window.URL.createObjectURL(blob);
            viewer.loadVrm(url);
          }
        });
      }
    },
    [viewer, selectedCharacter] // ✅ selectedCharacter를 의존성 배열에 추가
  );

  return (
    <div className={"w-full h-full -z-10"}>
      <canvas ref={canvasRef} className={"h-full w-full"}></canvas>
    </div>
  );
}
