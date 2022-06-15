document.addEventListener("DOMContentLoaded", ()=>{
    boxesTable = document.querySelector("#pills-all")
    boxesTable.replaceChildren()

    warehouseButtons = document.querySelectorAll(".js-select-warehouse")
    for (warehouseButton of warehouseButtons){
        warehouseButton.addEventListener("click", fetch_data)
    }

    function fetch_data(event){
        id = event.currentTarget.dataset.warehouse

        if (boxesTable.dataset.current == id){
            console.log("Repeated fetch attempted. Skipping.")
            return
        }
            

        fetch("warehouse/"+id).then((response) => response.json()).then((data)=>{
            console.log("New data arrived... rebuilding DOM")
            boxesTable.dataset.current = id
            boxPills = []
            for (box of data.boxes){
                outerContainer = document.createElement("a")
                outerContainer.classList.add("row", "text-decoration-none", "py-3", "px-4", "mt-5", "SelfStorage__boxlink")
                floorCodeContainer = document.createElement("div")
                floorCodeContainer.classList.add("col-12", "col-md-4", "col-lg-3", "d-flex", "justify-content-center", "align-items-center")
                floorSpan = document.createElement("span")
                floorSpan.classList.add("SelfStorage_green", "fs_24", "me-2")
                floorSpan.textContent = box.floor + " эт."
                codeSpan = document.createElement("span")
                codeSpan.classList.add("fs_24")
                codeSpan.textContent = box.code

                floorCodeContainer.appendChild(floorSpan)
                floorCodeContainer.appendChild(codeSpan)


                areaContainer = document.createElement("div")
                areaContainer.classList.add("col-6", "col-md-4", "col-lg-3", "d-flex", "justify-content-center", "align-items-center")
                areaSpan = document.createElement("span")
                areaSpan.classList.add("fs_24")
                areaSpan.textContent = box.area + " м²"

                areaContainer.appendChild(areaSpan)
                

                dimensionsContainer = document.createElement("div")
                dimensionsContainer.classList.add("col-6", "col-md-4", "col-lg-3", "d-flex", "justify-content-center", "align-items-center")
                dimensionsSpan = document.createElement("span")
                dimensionsSpan.classList.add("fs_24")
                dimensionsSpan.textContent = box.dimensions + " м"

                dimensionsContainer.appendChild(dimensionsSpan)


                rateContainer = document.createElement("div")
                rateContainer.classList.add("col-12", "col-lg-3")
                rateSpan = document.createElement("span")
                rateSpan.classList.add("btn", "my-2", "w-100", "text-white", "fs_24", "SelfStorage__bg_orange", "SelfStorage__btn2_orange", "border-8")
                rateSpan.textContent = box.rate + " ₽"

                rateContainer.appendChild(rateSpan)


                outerContainer.appendChild(floorCodeContainer)
                outerContainer.appendChild(areaContainer)
                outerContainer.appendChild(dimensionsContainer)
                outerContainer.appendChild(rateContainer)
                boxPills.push(outerContainer)
            }

            boxesTable.replaceChildren(...boxPills)
        })
    }
})