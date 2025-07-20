export const NewMessageDot = ({ topPx, rightPx }) => {
    return (
        <div className="badge" style={
            {
                position: "absolute",
                top: topPx,
                right: rightPx,
                backgroundColor: "#32a852",
                color: "white",
                borderRadius: "50%",
                padding: "5px",
                fontSize: "10px",
                width: "15px",
                height: "15px",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                zIndex: "10000"
            }
        }></div>
    )
}