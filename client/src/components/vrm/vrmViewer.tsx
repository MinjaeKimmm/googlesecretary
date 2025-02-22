import { useContext, useCallback, useEffect } from "react";
import { ViewerContext } from "../../features/vrmViewer/viewerContext";

interface VrmViewerProps {
  selectedModel: string;
}

export default function VrmViewer() {
  const { viewer } = useContext(ViewerContext);

  const modelUrls: Record<string, string> = {
    Bunny: "/models/bunny.vrm",
    Shortcut: "/models/shortcut.vrm",
    Wolf: "/models/wolf.vrm",
    Teenager: "/models/teenager.vrm",
    Tuxedo: "/models/tuxedo.vrm",
    Yukata: "/models/yukata.vrm",
  };

  // useEffect(() => {
  //   if (viewer && selectedModel) {
  //     console.log(`🔄 모델 변경: ${selectedModel}`);
  //     const modelUrl = modelUrls[selectedModel] || "/models/dummy.vrm";
  //     viewer.loadVrm(modelUrl);
  //   }
  // }, [selectedModel, viewer]);
  

  const canvasRef = useCallback(
    (canvas: HTMLCanvasElement) => {
      if (canvas) {
        viewer.setup(canvas);
        viewer.loadVrm("/models/dummy.vrm");

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
    [viewer]
  );

  return (
    <div className={"absolute top-0 left-0 w-screen h-1/2 -z-10"}>
      <canvas ref={canvasRef} className={"h-full w-full"}></canvas>
    </div>
  );
}
