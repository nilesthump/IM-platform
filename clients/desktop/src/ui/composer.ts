export function resizedComposerHeight(height:number,startY:number,currentY:number){return Math.max(42,Math.min(150,height+startY-currentY));}
